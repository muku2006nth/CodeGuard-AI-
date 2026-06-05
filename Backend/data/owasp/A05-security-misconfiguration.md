# OWASP Top 10: A05:2021 – Security Misconfiguration

The application might be vulnerable if the application is missing appropriate security hardening across any part of the application stack, or improperly configured permissions on cloud services, unnecessary features are enabled or installed (e.g. unnecessary ports, services, pages, accounts, or privileges), default accounts and their passwords are still enabled and unchanged, error handling reveals stack traces or other overly informative error messages to users, the software is out of date or vulnerable.

## Description

Security misconfiguration is commonly a result of insecure default configurations, incomplete or ad hoc configurations, open cloud storage, misconfigured HTTP headers, and verbose error messages containing sensitive information. Not only must all operating systems, frameworks, libraries, and applications be securely configured, but they must be patched and upgraded in a timely fashion. Common CWEs include CWE-16 Configuration, CWE-611 Improper Restriction of XML External Entity Reference.

## Prevention

- A repeatable hardening process makes it fast and easy to deploy another environment that is properly locked down. Development, QA, and production environments should all be configured identically, with different credentials used in each environment
- A minimal platform without any unnecessary features, components, documentation, and samples. Remove or do not install unused features and frameworks
- A task to review and update the configurations appropriate to all security notes, updates, and patches as part of the patch management process
- A segmented application architecture provides effective and secure separation between components or tenants, with segmentation, containerization, or cloud security groups
- Sending security directives to clients, e.g., Security Headers
- An automated process to verify the effectiveness of the configurations and settings in all environments
