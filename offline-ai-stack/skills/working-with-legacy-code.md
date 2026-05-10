# Skill: Working with Legacy Code
1. Characterize before you change. Add tests that pin current behavior — *especially* the weird parts. Those are the contract.
2. Don't refactor and feature-add in the same PR. Sequence: characterize → refactor under green tests → add feature.
3. Resist the urge to rewrite. Rewrites underestimate the implicit knowledge encoded in the existing code.
4. Use seams (Michael Feathers): break dependencies via parameters, subclasses, or environment overrides — not by editing the legacy callee.
5. When you must touch un-tested code, leave it more testable than you found it. Minimum: extract a function, add one test.
6. Read the git log of the file. Old comments and ancient hacks usually have a story; don't delete them blind.
