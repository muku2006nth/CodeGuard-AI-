# OWASP Top 10: A03:2021 – Injection

Injection flaws, such as SQL, NoSQL, OS, and LDAP injection, occur when untrusted data is sent to an interpreter as part of a command or query. The attacker's hostile data can trick the interpreter into executing unintended commands or accessing data without proper authorization.

## SQL Injection

SQL injection occurs when an attacker can insert or manipulate SQL queries in an application. The most common form is when user input is directly concatenated into SQL statements. For example, using string formatting like f"SELECT * FROM users WHERE id = {user_input}" is extremely dangerous. An attacker can supply input like "1 OR 1=1" to bypass authentication, or use UNION SELECT statements to extract data from other tables. Blind SQL injection variants allow data extraction through timing attacks or boolean conditions even when query results are not directly visible. Second-order SQL injection stores malicious input that is later used in a query.

## Command Injection

OS command injection occurs when an application passes unsafe user-supplied data to a system shell. Functions like os.system(), subprocess with shell=True, exec(), and eval() are particularly dangerous when used with untrusted input. An attacker can chain commands using operators like semicolons, pipes, backticks, or $() syntax to execute arbitrary commands. This can lead to complete server compromise, data exfiltration, or lateral movement within a network.

## Cross-Site Scripting (XSS)

XSS attacks inject malicious scripts into web pages viewed by other users. Reflected XSS bounces malicious scripts off a web application to victims. Stored XSS persists malicious scripts on the target server. DOM-based XSS occurs entirely on the client side. All variants can lead to session hijacking, defacement, redirection to malicious sites, or keylogging. Prevention requires context-aware output encoding, Content Security Policy headers, and frameworks that auto-escape by default.

## Path Traversal

Path traversal (directory traversal) attacks use sequences like "../" to access files and directories stored outside the intended folder. For example, an attacker might request "../../etc/passwd" to read sensitive system files. Applications that construct file paths using user input without proper validation are vulnerable. Functions like open(user_input), os.path.join with unchecked input, and file serving endpoints are common attack vectors.

## Deserialization

Insecure deserialization occurs when applications deserialize data from untrusted sources without validation. In Python, pickle.loads() on untrusted data can execute arbitrary code. Java ObjectInputStream, PHP unserialize(), and .NET BinaryFormatter are similarly dangerous. Attackers craft malicious serialized objects that execute code upon deserialization, potentially leading to remote code execution, replay attacks, injection attacks, and privilege escalation.

## Prevention

- Use safe APIs and parameterized queries. Prefer ORM frameworks that handle escaping automatically
- Positive server-side input validation with allowlists rather than denylists
- Escape special characters for the target interpreter using the specific escape syntax
- Use LIMIT and other SQL controls to prevent mass disclosure in case of SQL injection
- For OS commands, avoid shell=True and use subprocess with argument lists instead
- Implement Content Security Policy (CSP) headers to mitigate XSS
- Validate and sanitize file paths, use chroot jails or restricted base directories
- Avoid deserializing untrusted data. If necessary, use safe serialization formats like JSON instead of pickle or Java serialization
- Implement integrity checks such as digital signatures on serialized objects
