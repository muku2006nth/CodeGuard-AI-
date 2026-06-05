# OWASP Top 10: A01:2021 – Broken Access Control

Access control enforces policy such that users cannot act outside of their intended permissions. Failures typically lead to unauthorized information disclosure, modification, or destruction of data, or performing a business function outside the user's limits.

## Description

Broken access control is the most serious web application security risk. Common access control vulnerabilities include: violation of the principle of least privilege, bypassing access control checks by modifying the URL, internal application state, or HTML page, permitting viewing or editing someone else's account by providing its unique identifier (insecure direct object references), accessing APIs with missing access controls for POST, PUT, and DELETE, elevation of privilege (acting as a user without being logged in or acting as an admin when logged in as a user), metadata manipulation such as replaying or tampering with JWT access control tokens, or CORS misconfiguration allowing API access from unauthorized origins.

## Prevention

- Deny by default, except for public resources
- Implement access control mechanisms once and reuse throughout the application
- Model access controls should enforce record ownership
- Disable web server directory listing and ensure file metadata and backup files are not present within web roots
- Log access control failures and alert administrators when appropriate
- Rate limit API and controller access to minimize harm from automated attack tooling
- Stateless JWT tokens should be short-lived to minimize the window for an attacker
- Developers and QA staff should include functional access control unit and integration tests
