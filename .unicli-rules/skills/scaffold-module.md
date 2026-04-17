# Skill: scaffold-module

Generate the basic structure for a new module or package. Follow project conventions and create boilerplate only — do not fill in business logic.

## When to Use

- Adding a new domain module.
- Cloning an existing pattern to create a similar module.

## Steps

1. Check naming and directory conventions in `.unicli-rules/memory/conventions.md`.
2. Pick one existing similar module as a reference template.
3. Create the minimum set of files:
   - Entry point (`index.*` or `__init__.*`)
   - Type or interface definitions
   - Test skeleton
4. Leave a `TODO(scaffold):` comment in each generated file to mark where implementation is still needed.
5. Confirm the build still passes.

## Output

- List of files that were created.
- Recommendation for the next implementation step.
