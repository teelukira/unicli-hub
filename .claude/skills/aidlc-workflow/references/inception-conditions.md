# Inception Stage Conditional Execution Rules

## Reverse Engineering
**Execute IF**: project_type = brownfield AND `aidlc-docs/inception/reverse-engineering/` is empty/absent
**Skip IF**: project_type = greenfield OR reverse-engineering artifacts already exist

## User Stories
**Execute IF (ALWAYS)**: New user-facing features; multi-persona; complex acceptance criteria; customer-facing API
**Execute IF (LIKELY)**: Modifications to existing user-facing features; integration impacting user workflows
**Skip ONLY IF**: Pure internal refactoring; simple isolated bug fix; infra-only; documentation-only; developer tooling

## Application Design
**Execute IF**: New components/services needed; component methods/business rules need definition; component dependencies need clarification
**Skip IF**: Changes within existing component boundaries; no new components/methods; pure implementation changes

## Units Generation
**Execute IF**: System needs decomposition into multiple units; multiple services/modules required; complex system requiring structured breakdown
**Skip IF**: Single simple unit; no decomposition needed; straightforward single-component implementation
