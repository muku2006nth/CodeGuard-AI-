# OWASP Top 10: A06:2021 – Vulnerable and Outdated Components

Using components with known vulnerabilities, such as libraries, frameworks, and other software modules running with the same privileges as the application. If a vulnerable component is exploited, such an attack can facilitate serious data loss or server takeover. Applications and APIs using components with known vulnerabilities may undermine application defenses and enable various attacks and impacts.

## Description

You are likely vulnerable if you do not know the versions of all components you use (both client-side and server-side), if the software is vulnerable, unsupported, or out of date, if you do not scan for vulnerabilities regularly, if you do not fix or upgrade the underlying platform, frameworks, and dependencies in a risk-based, timely fashion, if software developers do not test the compatibility of updated, upgraded, or patched libraries.

## Prevention

- Remove unused dependencies, unnecessary features, components, files, and documentation
- Continuously inventory the versions of both client-side and server-side components and their dependencies using tools like OWASP Dependency-Check, retire.js
- Continuously monitor sources like CVE and NVD for vulnerabilities in your components
- Only obtain components from official sources over secure links. Prefer signed packages
- Monitor for libraries and components that are unmaintained or do not create security patches for older versions


# OWASP Top 10: A07:2021 – Identification and Authentication Failures

Confirmation of the user's identity, authentication, and session management is critical to protect against authentication-related attacks. Application functions related to authentication and session management are often implemented incorrectly, allowing attackers to compromise passwords, keys, or session tokens, or to exploit other implementation flaws to assume other users' identities temporarily or permanently.

## Description

There may be authentication weaknesses if the application permits automated attacks such as credential stuffing, permits brute force, permits default or weak passwords, uses weak credential recovery processes, uses plain text or weakly hashed passwords, has missing or ineffective multi-factor authentication, exposes session identifier in the URL, reuses session identifiers after successful login, or does not correctly invalidate sessions.

## Prevention

- Where possible, implement multi-factor authentication
- Do not ship or deploy with any default credentials, particularly for admin users
- Implement weak password checks against a list of the top 10,000 worst passwords
- Align password length, complexity and rotation policies with NIST 800-63b guidelines
- Harden against account enumeration attacks by using the same messages for all outcomes
- Limit or increasingly delay failed login attempts. Log all failures and alert administrators
- Use a server-side, secure, built-in session manager that generates a new random session ID with high entropy after login


# OWASP Top 10: A08:2021 – Software and Data Integrity Failures

Software and data integrity failures relate to code and infrastructure that does not protect against integrity violations. An example of this is where an application relies upon plugins, libraries, or modules from untrusted sources, repositories, and content delivery networks (CDNs). An insecure CI/CD pipeline can introduce the potential for unauthorized access, malicious code, or system compromise. Auto-update functionality where updates are downloaded without sufficient integrity verification and applied to the previously trusted application.

## Prevention

- Use digital signatures or similar mechanisms to verify the software or data is from the expected source
- Ensure libraries and dependencies are consuming trusted repositories
- Ensure that a software supply chain security tool, such as OWASP Dependency Check, is used to verify that components do not contain known vulnerabilities
- Ensure that there is a review process for code and configuration changes to minimize the chance that malicious code or configuration could be introduced


# OWASP Top 10: A09:2021 – Security Logging and Monitoring Failures

This category helps detect, escalate, and respond to active breaches. Without logging and monitoring, breaches cannot be detected. Insufficient logging, detection, monitoring, and active response occurs when auditable events are not logged, warnings and errors generate no or inadequate log messages, logs are not monitored for suspicious activity, logs are only stored locally.

## Prevention

- Ensure all login, access control, and server-side input validation failures can be logged with sufficient user context
- Ensure that logs are generated in a format that log management solutions can easily consume
- Ensure log data is encoded correctly to prevent injections or attacks on the logging or monitoring systems
- Ensure high-value transactions have an audit trail with integrity controls
- Establish or adopt an incident response and recovery plan


# OWASP Top 10: A10:2021 – Server-Side Request Forgery (SSRF)

SSRF flaws occur whenever a web application is fetching a remote resource without validating the user-supplied URL. It allows an attacker to coerce the application to send a crafted request to an unexpected destination, even when protected by a firewall, VPN, or another type of network access control list (ACL). Attackers can access internal services, read cloud metadata endpoints, scan internal networks, or perform remote code execution.

## Prevention

- Sanitize and validate all client-supplied input data
- Enforce the URL schema, port, and destination with a positive allow list
- Do not send raw responses to clients
- Disable HTTP redirections
- Be aware of the URL consistency to avoid attacks such as DNS rebinding and TOCTOU race conditions
