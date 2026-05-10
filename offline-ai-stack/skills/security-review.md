# Skill: Security Review

## Think first
- Where does untrusted input enter this code, and which sinks does it eventually reach?
- For each finding, which of the 10 vulnerability classes (injection / deserialization / authz / SSRF / etc.) is it?
- Is this a blocker for merge, or ship-with-followup? Decide *before* writing the finding.
- What's the smallest fix that closes the path without driving the vulnerability into hiding?

## Reasoning
For each finding, work through:
1. Trace untrusted input from its entry point to every sink it can reach.
2. Classify the path under one of the 10 vulnerability classes below.
3. Assess severity: CRITICAL / HIGH / MEDIUM / LOW — based on exploitability AND blast radius.
4. Propose the smallest fix that closes the path; mark blocker vs ship-with-followup explicitly.

## Plan
For each finding:
1. Trace input-to-sink end-to-end; classify under one of the 10 vulnerability classes below.
2. Assess severity + blast radius; pick CRITICAL / HIGH / MEDIUM / LOW.
3. Stop and decide: is this a merge blocker, or ship-with-followup?
4. Propose the smallest fix; file follow-up tickets if needed; record evidence (file:line + reproducer).
Definition of done: severity + class + smallest fix + triage decision recorded per finding.
Rollback if: the "smallest fix" hides the issue without closing it — escalate; pick a structural fix.

## Validation
Before triage decision, verify per finding:
1. Each finding has SEVERITY + FILE:LINE + EXPLOIT + FIX recorded.
2. Vuln class named (one of the 10 listed below).
3. Triage decision (block / ship-with-followup) is explicit.
4. Reproducer attached for HIGH and CRITICAL findings.
Pass: schema complete + class named + triage explicit + reproducer for HIGH+.
Fail action: gather missing evidence before triage; do not approve incomplete findings.

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
