# Skill: Security Review

Audit the code for these specific vulnerability classes. For each finding, report:
SEVERITY (CRITICAL / HIGH / MEDIUM / LOW), FILE:LINE, EXPLOIT, FIX.

1. **Command injection**
   - subprocess.run(..., shell=True) with unsanitized input
   - os.system(), os.popen() with user input
   - eval/exec of shell-formatted strings

2. **Code execution sinks**
   - eval(), exec(), Function constructor, new Function()
   - JSON parsers that allow function references
   - Template engines with code execution (Jinja2 sandbox bypass)

3. **XSS vectors**
   - dangerouslySetInnerHTML in React with user input
   - element.innerHTML = user_input
   - v-html in Vue, {@html} in Svelte
   - Markdown rendering without sanitization

4. **Unsafe deserialization**
   - pickle.loads, pickle.load (Python)
   - yaml.load (use yaml.safe_load)
   - Marshal, ObjectInputStream
   - JSON parsers configured to instantiate classes

5. **Path traversal**
   - open(user_input), Path(user_input)
   - Concatenation of user input into file paths without resolve()/normalize()
   - Zip/tar extraction without member-name validation (zip-slip)

6. **SQL injection**
   - String-formatted queries (f"SELECT ... {var}")
   - .format() into queries
   - Missing parameterization in ORM raw() calls

7. **Hardcoded secrets**
   - API keys, tokens, passwords, private keys in source
   - Default credentials in config defaults
   - Secrets in test fixtures committed to git

8. **AuthN/AuthZ bypasses**
   - Routes missing auth middleware
   - IDOR (object access by ID without ownership check)
   - JWT verification with `algorithms=['none']` or no `verify_signature`
   - Privilege checks that compare strings without canonicalization

9. **SSRF**
   - HTTP clients fetching user-supplied URLs without allowlist
   - Cloud metadata endpoint reachability (169.254.169.254)

10. **Open redirect**
    - Redirects to user-supplied URLs without origin check

End with a triage recommendation: which findings block merge, which can ship with follow-up tickets.
