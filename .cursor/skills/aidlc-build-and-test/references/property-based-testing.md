# Property-Based Testing — Reference Pointer

Read `.unicli-rules/extensions/testing/property-based/property-based-testing.md` for PBT rules. Load ONLY when Property-Based Testing extension is Enabled (Full).

Key requirement: jqwik property-based tests for domain logic.

Key summary:
- Framework: jqwik (Java) — `@Property`, `@ForAll`, `@Provide`
- Scope: domain service methods, value object invariants, boundary conditions
- Minimum: at least one `@Property` test per domain service class
- Required property categories:
  - Roundtrip properties (serialize → deserialize → equals)
  - Invariant properties (business rules hold for all valid inputs)
  - Boundary properties (edge values never cause unexpected exceptions)
- PBT tests live in `domain/src/test/` alongside unit tests
- qa-tester report must confirm jqwik tests ran and passed
- Missing PBT when extension is Enabled (Full) = BLOCKING finding
