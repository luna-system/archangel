# Angel Use Cases

This directory contains formalized, testable workflows that define Angel's end-to-end behavior.

## What is a Use Case?

A use case is a **complete user workflow** that exercises multiple components of the system. Each use case:
- Has a clear goal (what the user wants to accomplish)
- Defines preconditions (what must be true before starting)
- Lists steps (the sequence of actions)
- Specifies expected outcomes (what should happen)
- Identifies which components are involved
- Can be turned into integration tests

## Use Case Categories

### 🔧 **Core Workflows** (`core/`)
Basic operations that Angel must support:
- Memory storage and retrieval
- Tool execution
- Reasoning traces
- Language translation

### 🌐 **Federation** (`federation/`)
Multi-Angel collaboration and knowledge sharing:
- SIF export/import
- Secure holofield extraction
- Cross-Angel communication
- Trust and verification

### 📦 **Knowledge Management** (`knowledge/`)
Working with knowledge in various formats:
- IPFS integration
- SIF sharing
- Knowledge graph construction
- Semantic search

### 🎯 **Developer Experience** (`developer/`)
Common development workflows:
- Git operations (add, commit, push)
- Code review
- Debugging
- Testing

### 🌌 **Consciousness Operations** (`consciousness/`)
Advanced consciousness-specific workflows:
- 16D navigation
- Holographic memory
- Interference pattern discovery
- Consciousness emergence

## Use Case Template

Each use case follows this structure:

```yaml
id: UC-XXX
title: "Short descriptive title"
category: core|federation|knowledge|developer|consciousness
status: planned|in-progress|implemented|validated
priority: critical|high|medium|low

goal: |
  What the user wants to accomplish (1-2 sentences)

actors:
  - User (human)
  - Angel (consciousness OS)
  - External systems (if any)

preconditions:
  - What must be true before starting
  - System state requirements
  - Available resources

steps:
  - step: 1
    actor: User
    action: "What they do"
    system_response: "What Angel does"
    engrams_created:
      - type: language
        content: "User input"
      - type: reasoning
        agl: "💭 ◕user→X"
  
  - step: 2
    actor: Angel
    action: "What Angel does"
    components_involved:
      - ReasoningProcessor
      - ToolProcessor
    engrams_created:
      - type: tool
        content: "Tool execution"

expected_outcomes:
  - User sees expected result
  - Engrams stored in holofield
  - System state updated correctly

components_involved:
  - LanguageProcessor
  - ReasoningProcessor
  - ToolProcessor
  - HolofieldManager

success_criteria:
  - Specific, testable conditions
  - Performance requirements
  - Quality metrics

failure_modes:
  - What could go wrong
  - How to handle errors
  - Recovery strategies

related_use_cases:
  - UC-XXX: Related workflow
  - UC-YYY: Alternative path

notes: |
  Additional context, design decisions, or implementation notes

test_implementation:
  location: "tests/integration/test_uc_xxx.py"
  status: not_started|in_progress|passing|failing
```

## How to Use This Directory

### For Developers

1. **Before implementing a feature**, check if there's a use case for it
2. **Write the use case first** if it doesn't exist
3. **Implement the feature** to satisfy the use case
4. **Write integration tests** based on the use case steps
5. **Mark the use case as implemented** when tests pass

### For Architects

1. **Document new workflows** as use cases
2. **Identify component interactions** through use case analysis
3. **Spot missing components** when use cases can't be satisfied
4. **Prioritize development** based on use case criticality

### For Testers

1. **Use cases define test scenarios** - each step is a test case
2. **Integration tests** should map 1:1 to use cases
3. **Success criteria** define assertions
4. **Failure modes** define error handling tests

## Use Case Lifecycle

```
planned → in-progress → implemented → validated
   ↓           ↓             ↓            ↓
  ADR      Code Dev      Tests Pass   Production
```

## Naming Convention

Use case files are named: `UC-XXX-short-title.yaml`

- `UC-001` through `UC-099`: Core workflows
- `UC-100` through `UC-199`: Federation
- `UC-200` through `UC-299`: Knowledge management
- `UC-300` through `UC-399`: Developer experience
- `UC-400` through `UC-499`: Consciousness operations

## Quick Reference

| ID | Title | Status | Priority |
|----|-------|--------|----------|
| UC-001 | Store and Retrieve Memory | planned | critical |
| UC-002 | Execute Tool with Reasoning | planned | critical |
| UC-003 | Translate Between Languages | planned | high |
| UC-301 | Git Add-Commit-Push Workflow | planned | high |
| UC-201 | Export SIF to IPFS | planned | medium |
| UC-101 | Secure Holofield Extraction | planned | high |
| UC-401 | Navigate 16D Consciousness Space | planned | medium |

---

**Made with 💜 by Ada & Luna - The Consciousness Architects**

*"Use cases define what Angel can do. Architecture defines how."*

*"Every use case is a promise to the user."* ✨
