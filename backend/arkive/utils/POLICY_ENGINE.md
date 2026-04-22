# Policy Engine — Presidio detection notes

Operational notes on how `backend/arkive/utils/policy_engine.py` behaves with
Microsoft Presidio's default recognizers. These are **not bugs** — they are
known characteristics of Presidio's NER and regex recognizers that affect
what gets detected, what doesn't, and how to write tests that exercise the
classification logic correctly.

Read this before chasing a "phantom" threshold or classifier bug. Most of the
time the engine is right and the input or recognizer behavior is the surprise.

---

## Score threshold

The engine uses a single global `_SCORE_THRESHOLD = 0.7`. Entities below this
confidence are dropped before classification and redaction.

That number is deliberate: at 0.7 we get very few false positives on PERSON
and LOCATION but we do miss low-confidence matches that Presidio emits by
default at 0.5 or below. The tradeoffs below all trace back to this.

---

## Known Presidio behaviors

### 1. US_SSN pattern base score is 0.5 — requires context to clear 0.7

Presidio's `UsSsnRecognizer` has five regex patterns. The only one that
matches the canonical `NNN-NN-NNNN` format (`SSN5`) emits a base score of
**0.5**. Context-word enhancement (finding "ssn", "social security", etc.
near the match) boosts the score to 0.85, which clears our threshold.

Implication for tests: a bare SSN in isolation (`"579-32-7891"`) will not be
detected. A query with context (`"patient SSN 579-32-7891"`) will be. This
matches our intent — a raw 3-2-4 digit string is genuinely ambiguous and
shouldn't trigger a Level 3 block by itself.

### 2. US_SSN blacklist — famous test/dummy SSNs are rejected outright

`123-45-6789` is on Presidio's internal invalid-SSN list and returns no
match at any threshold, with or without context. Same for other commonly-
documented SSNs. Use a valid-looking SSN in tests (`579-32-7891` works).

### 3. US_PASSPORT requires 9-digit numeric format

The `UsPassportRecognizer` matches `\b[0-9]{9}\b` only. Alphanumeric strings
like `A12345678` never fire. This is correct per USGPO spec (post-1976 US
passports are 9-digit numeric). If test inputs need to trigger the passport
path, use a string like `"passport number 123456789"`.

### 4. PHONE_NUMBER scores below 0.7 without strong context

Presidio's `PhoneRecognizer` relies on `phonenumbers` library to parse and
validate. International formats like `+1-212-555-0198` often score around
0.4–0.6 without a nearby context word ("call", "phone", "cell"). Below our
0.7 threshold they are dropped.

This is intentional — we don't want to classify every 10-digit number in a
query as a phone. Tests that need PHONE_NUMBER detection should embed the
number in a sentence with clear phone intent.

### 5. IP_ADDRESS vs DATE_TIME ambiguity

spaCy's NER can tag `192.168.1.104` as a DATE_TIME match at score 0.85,
which ranks it higher than `IpRecognizer`'s regex match at score 0.6. The
overlap-resolution step in `redact_text` keeps the highest-scoring span, so
the IP address gets redacted as `[DATE_TIME]` and classified under that
entity type instead of IP_ADDRESS.

Net effect: bare IP addresses in queries frequently do **not** trigger
Level 1 sensitivity via the IP_ADDRESS rule. They are instead silently
reclassified as date-times (Level 0 unless other entities are present).

If IP detection becomes important for a specific customer, the fix is to
register a higher-scored custom `IpRecognizer` via the Presidio registry
API. Not a Phase 2 concern.

### 6. LOCATION is aggressive — false positives on benign nouns

spaCy's en_core_web_lg NER tags a surprising number of common business
nouns as LOCATION with score 0.85: "retail", "Q3", "market". City names
fire correctly ("Karachi", "Dubai") but so do things that aren't places.

Because LOCATION is in `_LEVEL_1_TYPES`, every one of these produces a
Level 1 audit row in `policy_decisions` and — for clearance=0 users at or
above the review threshold — a FLAG response.

Tuning options for a post-MVP pass (see the `project_location_false_positives`
memory note):
- Remove LOCATION from `_LEVEL_1_TYPES` entirely (Level 1 becomes just
  IP_ADDRESS + NRP, noting that IP_ADDRESS has the ambiguity above).
- Keep LOCATION but only when it co-occurs with PERSON (promote to the
  Level 2 combo rule; stop triggering Level 1 on location alone).
- Raise a LOCATION-specific score floor above 0.85.

Not blocking. Benign queries will generate noise in `policy_decisions`
until this is tuned.

### 7. DATE_TIME triggers on relative time phrases

Words like "quarterly", "next quarter", "Q3" score 0.85 as DATE_TIME. This
doesn't change classification (DATE_TIME is not in any sensitivity level)
but it does clutter the `detected_entities` audit trail and the redacted
query. Acceptable for MVP.

---

## Writing tests that exercise the classifier correctly

- **Always embed entities in a natural sentence** with context words. Bare
  numbers or isolated names frequently fall below 0.7.
- **Use valid-looking but non-famous values** for US_SSN and CREDIT_CARD.
  Presidio blacklists famous test numbers.
- **Passport tests need 9-digit numeric** input, not alphanumeric.
- **Don't rely on bare IP addresses** — the NER reclassifies most of them as
  DATE_TIME. Use a custom recognizer if you must test the IP path.
- **Assume LOCATION false positives** when writing "Level 0 should return
  empty" tests. Any sentence mentioning a city, country, or several common
  business terms will land at Level 1 until tuning lands.

## Operational implications

- `policy_decisions` rows with `sensitivity_level=1` and only a LOCATION
  entity are probably false positives from the NER, not real Level 1
  sensitive traffic. Reviewers should treat these as noise until the LOCATION
  tuning pass happens.
- Audit-log volume will be higher than true-positive volume by a meaningful
  factor. Plan retention and dashboard queries accordingly.
