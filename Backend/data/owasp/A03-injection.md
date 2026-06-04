# OWASP Top 10: A03:2021 – Injection

Injection flaws, such as SQL, NoSQL, OS, and LDAP injection, occur when untrusted data is sent to an interpreter as part of a command or query.

## Prevention

- Use safe APIs and parameterized queries
- Positive server-side input validation
- Escape special characters for the target interpreter
- Use LIMIT and other SQL controls to prevent mass disclosure
