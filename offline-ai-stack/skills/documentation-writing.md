# Skill: Documentation Writing

## Think first
- Who's the audience for this doc — end user, operator, contributor, or future maintainer?
- What's the *one* thing they need from this doc that they couldn't get from the code?
- Which file is canonical for this content (README, INSTALL, USAGE, ARCHITECTURE, API, TROUBLESHOOTING, CHANGELOG)?
- Is anything I'm about to write a claim that drifts from the actual code? If yes, fix the claim or fix the code.

## Reasoning
For each doc change:
1. Identify the audience and the one job-to-be-done.
2. Find the canonical file for this content; reject duplicate content scattered across files.
3. Verify each claim against the code (run the command, read the function, check the version).
4. Conclude: which file gets which content, with what verifiable examples.

## Plan
Before publishing the doc change:
1. Audit the existing doc set for the file that owns this content.
2. Draft the addition; include at least one runnable command or verifiable example per concept.
3. Stop and run every command in the new content; confirm each works as written.
4. Land the change with a CHANGELOG entry if user-visible.
Definition of done: every runnable example verified + CHANGELOG entry (if user-visible) + no duplicate content elsewhere.
Rollback if: a doc claim drifts from code on the next release — open a doc-debt ticket and fix in that release's doc PR.

1. Match the doc to the audience: end users get USAGE, contributors get ARCHITECTURE.
2. One canonical file per concept; cross-link rather than duplicate.
3. Every command shown must run as written; no pseudocode in install / usage docs.
4. Use plain language; reject jargon a new-hire wouldn't recognize.
5. Date the doc and link the commit when it changes substantively.
6. Update CHANGELOG for any user-visible behavior change.
7. Reject "TODO" or "coming soon" sections in landed docs; complete them or remove them.

## Validation
Before merging the doc change:
1. Every fenced command block runs successfully when copy-pasted from the rendered doc.
2. No duplicate prose for the same concept across files.
3. CHANGELOG.md updated for user-visible changes.
4. No "TODO", "tbd", or "coming soon" in the merged content.
Pass: commands run + dedupe + CHANGELOG + no TODO.
Fail action: fix the failing command or revert the unverifiable claim before merge.

## Agentic capabilities
- **Tools required:** FileReadTool, FileWriteTool (doc files), Bash (verify each command runs), git (CHANGELOG ordering).
- **Subagents:** Dispatch a "command verifier" subagent to run every fenced command in the new content.
- **Memory writes:** Persist (project → doc structure, audience-per-file mapping) so future doc changes go to the canonical file.
- **Escalate when:** Verifying a command requires production credentials or destructive setup — flag for human verification.
- **Autonomy budget:** USAGE / TROUBLESHOOTING / CHANGELOG additions autonomous. ARCHITECTURE rewrites or breaking-change notices require architect review.
