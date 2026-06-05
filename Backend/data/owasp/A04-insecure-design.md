# OWASP Top 10: A04:2021 – Insecure Design

Insecure design is a broad category representing different weaknesses, expressed as missing or ineffective control design. Insecure design is not the source for all other Top 10 risk categories. There is a difference between insecure design and insecure implementation. A secure design can still have implementation defects leading to vulnerabilities that may be exploited. An insecure design cannot be fixed by a perfect implementation as by definition, needed security controls were never created to defend against specific attacks.

## Description

Insecure design focuses on risks related to design and architectural flaws, with a call for more use of threat modeling, secure design patterns, and reference architectures. Notable Common Weakness Enumerations include CWE-209 Generation of Error Message Containing Sensitive Information, CWE-256 Unprotected Storage of Credentials, CWE-501 Trust Boundary Violation, and CWE-522 Insufficiently Protected Credentials.

## Prevention

- Establish and use a secure development lifecycle with application security professionals to help evaluate and design security and privacy-related controls
- Establish and use a library of secure design patterns or paved road ready-to-use components
- Use threat modeling for critical authentication, access control, business logic, and key flows
- Integrate security language and controls into user stories
- Integrate plausibility checks at each tier of your application from frontend to backend
- Write unit and integration tests to validate that all critical flows are resistant to the threat model
- Segregate tier layers on the system and network layers depending on the exposure and protection needs
- Limit resource consumption by user or service
