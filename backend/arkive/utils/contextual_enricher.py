import os
import asyncio
import logging
import httpx

log = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
ENRICHMENT_TIMEOUT = 30.0
ENRICHMENT_CONCURRENCY = 5  # max parallel Ollama calls

ENRICHMENT_PROMPT = """You are a document indexing assistant.
Your job is to write 1-2 sentences that describe what the 
following chunk is about and how it fits within the document 
titled "{document_title}".

Be specific — mention the topic, key entities, and purpose.
Do not use phrases like "this chunk" or "this section".
Write as if labeling the content for a search index.

Chunk content:
{chunk_content}

Write the 1-2 sentence description only. Nothing else."""


async def _enrich_single_chunk(
    chunk_content: str,
    document_title: str,
    semaphore: asyncio.Semaphore,
) -> str:
    """
    Calls Ollama to generate a context description for one chunk.
    Prepends the description to the chunk content.
    Falls back to original chunk content on any failure.
    Never raises.
    """
    async with semaphore:
        try:
            prompt = ENRICHMENT_PROMPT.format(
                document_title=document_title,
                chunk_content=chunk_content[:2000],
            )

            openai_payload = {
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "temperature": 0.0,
            }

            native_payload = {
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.0},
            }

            context_summary = None

            async with httpx.AsyncClient(timeout=ENRICHMENT_TIMEOUT) as client:
                try:
                    response = await client.post(
                        f"{OLLAMA_BASE_URL}/v1/chat/completions",
                        json=openai_payload,
                    )
                    response.raise_for_status()
                    data = response.json()
                    context_summary = (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                        .strip()
                    )
                except httpx.HTTPStatusError as e:
                    if e.response.status_code != 404:
                        raise
                    # Fall back to native Ollama /api/chat endpoint
                    response = await client.post(
                        f"{OLLAMA_BASE_URL}/api/chat",
                        json=native_payload,
                    )
                    response.raise_for_status()
                    data = response.json()
                    context_summary = (
                        (data.get("message") or {})
                        .get("content", "")
                        .strip()
                    )

            if not context_summary:
                return chunk_content

            enriched = f"{context_summary}\n\n{chunk_content}"
            log.debug(
                f"[enricher] enriched chunk "
                f"({len(chunk_content)} → {len(enriched)} chars)"
            )
            return enriched

        except httpx.TimeoutException:
            log.warning("[enricher] timeout — using original chunk")
            return chunk_content
        except Exception as e:
            log.warning(f"[enricher] failed: {e} — using original chunk")
            return chunk_content


async def enrich_chunks(
    docs: list,
    document_title: str,
) -> list:
    """
    Enriches a list of document chunks in parallel (max ENRICHMENT_CONCURRENCY
    concurrent Ollama calls).

    docs: chunked Document list from save_docs_to_vector_db().
          Each item is a langchain Document with .page_content (str)
          and .metadata (dict).

    document_title: injected into the prompt so the LLM knows which
                    document the chunk belongs to. Pass
                    doc.metadata.get('name', 'Unknown Document').

    Returns the same list with .page_content updated in-place.
    If enrichment fails for any chunk, that chunk is unchanged.
    If enrichment fails entirely, returns docs unchanged.
    Never raises.
    """
    if not docs:
        return docs

    semaphore = asyncio.Semaphore(ENRICHMENT_CONCURRENCY)

    try:
        enriched_contents = await asyncio.gather(
            *[
                _enrich_single_chunk(
                    chunk_content=doc.page_content,
                    document_title=document_title,
                    semaphore=semaphore,
                )
                for doc in docs
            ],
            return_exceptions=True,
        )

        for doc, result in zip(docs, enriched_contents):
            if isinstance(result, Exception):
                log.warning(
                    f"[enricher] chunk failed with exception: {result}"
                    " — keeping original"
                )
            elif isinstance(result, str):
                doc.page_content = result

        enriched_count = sum(
            1 for r in enriched_contents
            if isinstance(r, str) and r
        )
        log.info(
            f"[enricher] enriched {enriched_count}/{len(docs)} chunks "
            f"from '{document_title}'"
        )

    except Exception as e:
        log.exception(
            f"[enricher] batch enrichment failed: {e} "
            "— returning original chunks"
        )

    return docs
