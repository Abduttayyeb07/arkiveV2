import time

from fastapi.responses import JSONResponse

from arkive.utils.policy_engine import PolicyDecisionResult


####################
# Structured error responses
#
# Keep error envelopes consistent across the policy gate so clients can
# branch on `code` and surface `audit_id` to reviewers without parsing
# free-form `detail` strings.
####################


class PolicyDeniedException(Exception):
    def __init__(self, policy_result: PolicyDecisionResult):
        self.policy_result = policy_result


def policy_error_response(
    policy_result: PolicyDecisionResult,
    status_code: int = 403,
) -> JSONResponse:
    if policy_result.decision == 'block':
        code = 'POLICY_BLOCKED'
        message = policy_result.reason
    else:
        code = 'POLICY_FLAGGED'
        message = f'Your request has been flagged for review: {policy_result.reason}'

    return JSONResponse(
        status_code=status_code,
        content={
            'error': {
                'code': code,
                'type': 'policy_violation',
                'message': message,
                'decision': policy_result.decision,
                'sensitivity_level': policy_result.sensitivity_level,
                'audit_id': policy_result.audit_id,
                'timestamp': int(time.time()),
            }
        },
    )
