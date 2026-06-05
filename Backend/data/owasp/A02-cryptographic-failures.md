# OWASP Top 10: A02:2021 – Cryptographic Failures

Previously known as Sensitive Data Exposure, this category focuses on failures related to cryptography which often lead to sensitive data exposure or system compromise. Common flaws include use of hard-coded passwords, broken or risky cryptographic algorithms, and insufficient entropy.

## Description

The first thing is to determine the protection needs of data in transit and at rest. Passwords, credit card numbers, health records, personal information, and business secrets require extra protection. For all such data: is any data transmitted in clear text (HTTP, SMTP, FTP)? Are any old or weak cryptographic algorithms or protocols used? Are default crypto keys in use, weak crypto keys generated or re-used, or is proper key management or rotation missing? Is encryption not enforced? Is the received server certificate and the trust chain properly validated? Are initialization vectors ignored, reused, or not generated sufficiently secure? Is an insecure mode of operation being used? Are passwords being used as cryptographic keys in absence of a password base key derivation function? Is randomness used for cryptographic purposes that was not designed to meet cryptographic requirements?

## Prevention

- Classify data processed, stored, or transmitted by an application and identify which data is sensitive according to privacy laws, regulatory requirements, or business needs
- Don't store sensitive data unnecessarily. Discard it as soon as possible
- Make sure to encrypt all sensitive data at rest
- Ensure up-to-date and strong standard algorithms, protocols, and keys are in place; use proper key management
- Encrypt all data in transit with secure protocols such as TLS with forward secrecy (FS) ciphers, cipher prioritization by the server, and secure parameters
- Disable caching for responses that contain sensitive data
- Do not use legacy protocols such as FTP and SMTP for transporting sensitive data
- Store passwords using strong adaptive and salted hashing functions with a work factor (delay factor) such as Argon2, scrypt, bcrypt, or PBKDF2
- Always use authenticated encryption instead of just encryption
- Cryptographic keys should be generated cryptographically randomly and stored in memory as byte arrays
