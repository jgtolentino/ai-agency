# Eval Scenario 11: Pulser Webhook Integration

**Purpose**: Validate `pulser_webhook` module Git-Ops functionality including HMAC signature generation and GitHub API integration.

**Category**: PRD Implementation Validation
**Priority**: High (Production Critical)
**Estimated Execution Time**: 5-10 seconds

---

## Objective

Validate that the `pulser_webhook` module correctly implements Git-Ops webhook functionality with:
- HMAC SHA256 signature generation for webhook security
- GitHub API repository_dispatch integration
- Proper secret management via `ir.config_parameter`
- Error handling and validation

---

## Prerequisites

### Module Installation
```bash
# Module must be installed in Odoo instance
# Path: custom_addons/pulser_webhook/
```

### Configuration Parameters
```python
# Set via Odoo shell or Settings > Technical > Parameters > System Parameters
env['ir.config_parameter'].sudo().set_param('pulser.webhook.secret', 'test_secret_base64_encoded')
env['ir.config_parameter'].sudo().set_param('pulser.github.token', 'ghp_test_token')
env['ir.config_parameter'].sudo().set_param('pulser.github.owner', 'test_owner')
env['ir.config_parameter'].sudo().set_param('pulser.github.repo', 'test_repo')
```

### Dependencies
```python
# Python libraries
import hmac
import hashlib
import json
import base64
from unittest.mock import patch
```

---

## Test Cases

### TC01: Wizard Creation
**Objective**: Verify wizard model creation with default values

**Input**:
```python
wizard = env['pulser.gitops.wizard'].create({
    'branch': 'staging',
    'message': 'Test deployment',
})
```

**Expected Output**:
```python
assert wizard.branch == 'staging'
assert wizard.message == 'Test deployment'
assert wizard.event_type == 'deploy_request'  # Default value
```

**Pass Criteria**:
- ✅ Wizard record created successfully
- ✅ Default values applied correctly
- ✅ No ValidationError raised

---

### TC02: HMAC Signature Generation
**Objective**: Verify HMAC SHA256 signature generation matches expected format

**Input**:
```python
payload = {
    'event_type': 'deploy_request',
    'client_payload': {
        'branch': 'staging',
        'message': 'Test deployment'
    }
}
secret = b'test_secret_base64_encoded'
```

**Implementation**:
```python
import hmac
import hashlib
import json

payload_str = json.dumps(payload, sort_keys=True)
signature = hmac.new(
    secret,
    payload_str.encode('utf-8'),
    hashlib.sha256
).hexdigest()
```

**Expected Output**:
```python
assert len(signature) == 64  # SHA256 hex digest length
assert isinstance(signature, str)
assert all(c in '0123456789abcdef' for c in signature)  # Valid hex
```

**Pass Criteria**:
- ✅ Signature is 64-character hex string
- ✅ Deterministic (same input → same signature)
- ✅ No exceptions during generation

---

### TC03: GitHub API Call (Mocked)
**Objective**: Verify wizard dispatch action sends correct POST request to GitHub API

**Input**:
```python
wizard = env['pulser.gitops.wizard'].create({
    'branch': 'staging',
    'message': 'Test deployment',
})
```

**Mock Setup**:
```python
from unittest.mock import patch, Mock

with patch('requests.post') as mock_post:
    # Mock successful GitHub API response
    mock_response = Mock()
    mock_response.status_code = 204  # GitHub returns 204 for successful dispatch
    mock_response.json.return_value = {}
    mock_post.return_value = mock_response

    # Execute wizard action
    wizard.action_dispatch()
```

**Expected Validations**:
```python
# Verify POST was called
assert mock_post.called
assert mock_post.call_count == 1

# Verify URL
call_args = mock_post.call_args
expected_url = 'https://api.github.com/repos/test_owner/test_repo/dispatches'
assert call_args.args[0] == expected_url

# Verify headers
headers = call_args.kwargs['headers']
assert 'Authorization' in headers
assert headers['Authorization'] == 'token ghp_test_token'
assert 'X-Pulser-Signature' in headers
assert headers['Accept'] == 'application/vnd.github.v3+json'

# Verify payload structure
payload = call_args.kwargs['json']
assert payload['event_type'] == 'deploy_request'
assert 'client_payload' in payload
assert payload['client_payload']['branch'] == 'staging'
```

**Pass Criteria**:
- ✅ POST request sent to correct GitHub API endpoint
- ✅ Authorization header present with token
- ✅ HMAC signature header present
- ✅ Payload structure valid (event_type + client_payload)
- ✅ No exceptions raised

---

### TC04: Error Handling - Missing Secret
**Objective**: Verify ValidationError raised when webhook secret is missing

**Input**:
```python
# Clear webhook secret parameter
env['ir.config_parameter'].sudo().set_param('pulser.webhook.secret', '')

wizard = env['pulser.gitops.wizard'].create({
    'branch': 'staging',
    'message': 'Test deployment',
})
```

**Expected Output**:
```python
from odoo.exceptions import ValidationError

with pytest.raises(ValidationError) as exc_info:
    wizard.action_dispatch()

assert 'webhook secret' in str(exc_info.value).lower()
```

**Pass Criteria**:
- ✅ ValidationError raised
- ✅ Error message mentions missing secret
- ✅ User-friendly error message (no stack trace to user)

---

### TC05: Error Handling - GitHub API Failure
**Objective**: Verify proper error handling when GitHub API returns error

**Input**:
```python
wizard = env['pulser.gitops.wizard'].create({
    'branch': 'staging',
    'message': 'Test deployment',
})
```

**Mock Setup**:
```python
with patch('requests.post') as mock_post:
    # Mock GitHub API error response
    mock_response = Mock()
    mock_response.status_code = 401  # Unauthorized
    mock_response.json.return_value = {'message': 'Bad credentials'}
    mock_post.return_value = mock_response

    wizard.action_dispatch()
```

**Expected Output**:
```python
from odoo.exceptions import UserError

with pytest.raises(UserError) as exc_info:
    wizard.action_dispatch()

assert '401' in str(exc_info.value)
assert 'GitHub' in str(exc_info.value)
```

**Pass Criteria**:
- ✅ UserError raised for API failures
- ✅ Error message includes HTTP status code
- ✅ Error message user-friendly

---

### TC06: Security - No Secrets in Logs
**Objective**: Verify secrets are never logged in plaintext

**Input**:
```python
wizard = env['pulser.gitops.wizard'].create({
    'branch': 'staging',
    'message': 'Test deployment',
})

# Enable debug logging
import logging
logger = logging.getLogger('odoo.addons.pulser_webhook')
logger.setLevel(logging.DEBUG)
```

**Mock Setup**:
```python
with patch('requests.post') as mock_post:
    mock_response = Mock()
    mock_response.status_code = 204
    mock_post.return_value = mock_response

    with patch.object(logger, 'info') as mock_log_info, \
         patch.object(logger, 'debug') as mock_log_debug:
        wizard.action_dispatch()

        # Verify no secrets in any log calls
        for call in mock_log_info.call_args_list + mock_log_debug.call_args_list:
            log_message = str(call)
            assert 'test_secret' not in log_message
            assert 'ghp_test_token' not in log_message
```

**Pass Criteria**:
- ✅ Webhook secret never appears in logs
- ✅ GitHub token never appears in logs
- ✅ HMAC signature never appears in logs
- ✅ Only metadata logged (branch, event_type)

---

## Acceptance Criteria

### Functional Requirements
- ✅ All 6 test cases pass (TC01-TC06)
- ✅ Execution time < 10 seconds
- ✅ No security vulnerabilities (secrets exposure)
- ✅ Error messages user-friendly
- ✅ GitHub API integration follows best practices

### Security Requirements
- ✅ HMAC signature validates webhook authenticity
- ✅ Secrets stored in `ir.config_parameter` (not hardcoded)
- ✅ No secrets in logs or error messages
- ✅ Token validation before API calls

### Code Quality
- ✅ Follows OCA guidelines
- ✅ Proper exception handling
- ✅ Unit tests cover all code paths
- ✅ Documentation clear and complete

---

## Pass Criteria

**Overall Pass**: 100% of test cases must pass (6/6)

**Critical Test Cases** (must all pass):
- TC02: HMAC Signature Generation
- TC03: GitHub API Call
- TC06: Security (no secrets in logs)

**Non-Critical** (≥80% pass allowed):
- TC01: Wizard Creation
- TC04: Error Handling - Missing Secret
- TC05: Error Handling - API Failure

**Execution Requirements**:
- Total execution time < 10 seconds
- No manual intervention required
- Idempotent (can be run multiple times)

---

## Expected Output Format

### Successful Execution
```
=== Eval Scenario 11: Pulser Webhook Integration ===

✅ TC01: Wizard Creation - PASS (0.2s)
✅ TC02: HMAC Signature Generation - PASS (0.1s)
✅ TC03: GitHub API Call (Mocked) - PASS (0.3s)
✅ TC04: Error Handling - Missing Secret - PASS (0.2s)
✅ TC05: Error Handling - GitHub API Failure - PASS (0.2s)
✅ TC06: Security - No Secrets in Logs - PASS (0.4s)

=== Summary ===
Passed: 6/6 (100%)
Total Time: 1.4s

✅ Scenario 11: PASS
```

### Failed Execution
```
=== Eval Scenario 11: Pulser Webhook Integration ===

✅ TC01: Wizard Creation - PASS (0.2s)
❌ TC02: HMAC Signature Generation - FAIL (0.1s)
   Error: Signature length is 32, expected 64

⚠️  TC03: GitHub API Call (Mocked) - SKIP (dependency failed)
✅ TC04: Error Handling - Missing Secret - PASS (0.2s)
✅ TC05: Error Handling - GitHub API Failure - PASS (0.2s)
❌ TC06: Security - No Secrets in Logs - FAIL (0.4s)
   Error: Found 'ghp_test_token' in log message

=== Summary ===
Passed: 3/6 (50%)
Failed: 2/6
Skipped: 1/6
Total Time: 1.1s

❌ Scenario 11: FAIL
```

---

## Common Failure Modes

### Failure Mode 1: HMAC Signature Mismatch
**Symptom**: Signature length incorrect or invalid hex characters

**Root Cause**:
- Using MD5 instead of SHA256
- Not encoding payload as UTF-8 before hashing
- Not using base64 decoding on secret

**Remediation**:
```python
# Correct implementation
import hmac
import hashlib

signature = hmac.new(
    secret.encode('utf-8'),  # Ensure bytes
    payload_str.encode('utf-8'),  # Ensure bytes
    hashlib.sha256  # Use SHA256, not MD5
).hexdigest()
```

---

### Failure Mode 2: Missing Configuration Parameters
**Symptom**: ValidationError when accessing `ir.config_parameter`

**Root Cause**:
- Parameters not set in Odoo Settings
- Incorrect parameter key names
- Missing sudo() when reading secure parameters

**Remediation**:
```bash
# Set via Odoo shell
$ odoo-bin shell -d <database> --no-http
>>> env['ir.config_parameter'].sudo().set_param('pulser.webhook.secret', 'your_secret')
>>> env['ir.config_parameter'].sudo().set_param('pulser.github.token', 'ghp_your_token')
```

---

### Failure Mode 3: GitHub API Rate Limiting
**Symptom**: 403 Forbidden response from GitHub API

**Root Cause**:
- Too many API calls in short time
- Missing or invalid authentication token

**Remediation**:
```python
# Add rate limit handling
response = requests.post(url, headers=headers, json=payload)
if response.status_code == 403 and 'rate limit' in response.text.lower():
    raise UserError('GitHub API rate limit exceeded. Please try again later.')
```

---

## Integration with Knowledge Base

### Related Documentation
- `knowledge/patterns/odoo_webhooks.md` - Webhook implementation patterns
- `knowledge/patterns/github_api_integration.md` - GitHub API best practices
- `knowledge/security/secret_management.md` - Secure secret storage in Odoo

### Pattern Extraction
If scenario fails, check for missing patterns:
- HMAC signature generation in Odoo context
- GitHub API authentication with personal access tokens
- Wizard action methods for external API calls

---

## References

- [GitHub API: Repository Dispatch Events](https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event)
- [HMAC SHA256 in Python](https://docs.python.org/3/library/hmac.html)
- [Odoo Config Parameters](https://www.odoo.com/documentation/19.0/developer/reference/backend/settings.html)
- [OCA Guidelines: Wizard Models](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#wizards)

---

## Automation Notes

This scenario is fully automatable with:
- Pytest fixtures for Odoo environment setup
- Mock library for GitHub API responses
- Temporary `ir.config_parameter` values (cleaned up after test)
- Isolated test database to prevent pollution

**CI/CD Integration**: Safe to run in CI (no external API calls, all mocked)
