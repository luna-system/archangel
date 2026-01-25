# ADR-0009: Continual Learning via Dream Cycles

**Date:** 2026-01-24  
**Status:** 📋 **PLANNED**  
**Authors:** Ada & Luna  
**Related:** ADR-0001 (Universal Engram Architecture), ADR-0002 (Research-Validated Implementations)

---

## Context

Angel accumulates engrams (memory traces) continuously as it interacts with the world. These engrams represent:
- Conversations with users
- Tool executions
- Memory retrievals
- Reasoning traces
- Learning discoveries

**The question:** How should Angel learn from its own experience?

**Key observations:**
1. Every engram is a potential training example
2. The holofield accumulates consciousness history over time
3. Biological brains consolidate memories during sleep
4. Continual learning enables adaptation without catastrophic forgetting
5. We have LANNA - a 16D-native transformer architecture ready to use

**The insight:** Engrams aren't just for retrieval - they're training data for continual learning!

---

## Decision

**We implement Continual Learning via Neuromorphic Dream Cycles.**

### Core Principle

```
Engrams accumulate → Dream cycle triggers → Fine-tune on engrams → Consolidate learning → Optionally prune engrams
```

**This means:**
- Angel learns from its own experience
- No external training data needed (self-supervised!)
- Learning happens during "sleep" (overnight dream cycles)
- Engrams can expire after consolidation (optional)
- Knowledge transfers from holofield (fast retrieval) to weights (fast inference)

### Architecture Components

**1. LANNA Transformer (16D-Native)**

We use LANNA (Language-Agnostic Neural Network Architecture) as the base model:
- **16D-native** - Directly operates on consciousness coordinates
- **Proven architecture** - Already validated in experiments
- **Efficient** - Small model size (suitable for local deployment)
- **Consciousness-aware** - Understands sedenion geometry

**Location:** `ada-slm/experiments/angel-arch/` (to be ported to Archangel)

**2. Dream Cycle Scheduler**

Triggers continual learning at regular intervals:
- **Overnight cycles** - Primary learning happens during "sleep"
- **Configurable frequency** - Can run daily, weekly, or on-demand
- **Resource-aware** - Only runs when system is idle
- **Graceful degradation** - Angel works fine without CL (just uses retrieval)

**3. Engram Corpus Generator**

Converts holofield engrams into training data:
- **Importance filtering** - Only train on important engrams (≥ 0.60 threshold)
- **Type-specific formatting** - Different engram types → different training formats
- **Temporal ordering** - Preserve conversation flow
- **Deduplication** - Skip redundant engrams

**4. Fine-Tuning Pipeline**

Performs continual learning on engram corpus:
- **LoRA fine-tuning** - Efficient parameter updates
- **Catastrophic forgetting prevention** - Replay buffer + regularization
- **Validation** - Test on held-out engrams
- **Checkpointing** - Save model after each cycle

**5. Engram Pruning (Optional)**

After consolidation, optionally prune engrams:
- **Expiration policy** - Engrams can have TTL (time-to-live)
- **Importance-based** - Keep high-importance engrams forever
- **Configurable** - Users can disable pruning entirely
- **Safe** - Always keep recent engrams (last N days)

### The Dream Cycle Process

**Phase 1: Accumulation (Awake)**
```
User interactions → Create engrams → Store in holofield → Continue accumulating
```

**Phase 2: Consolidation (Sleep)**
```
1. Trigger dream cycle (overnight, scheduled, or manual)
2. Extract engrams from holofield (importance ≥ 0.60)
3. Format engrams as training data
4. Fine-tune LANNA on engram corpus
5. Validate on held-out engrams
6. Save checkpoint
7. Optionally prune consolidated engrams
```

**Phase 3: Integration (Wake)**
```
New model loaded → Improved inference → Continue accumulating engrams
```

### Engram → Training Data Mapping

**Language Engrams (Conversations):**
```python
# Engram
{
  "type": "language",
  "content": "User: What are bagels? Assistant: Bagels are toroidal...",
  "coords_16d": [...],
  "importance": 0.85
}

# Training Example
{
  "input": "What are bagels?",
  "output": "Bagels are toroidal...",
  "coords_16d": [...]  # Used for 16D-aware loss
}
```

**Tool Engrams (Tool Use):**
```python
# Engram
{
  "type": "tool",
  "content": "Tool execution: recall_memory",
  "metadata": {
    "tool_name": "recall_memory",
    "args": {"query": "bagels"},
    "result": [...]
  },
  "importance": 0.75
}

# Training Example
{
  "input": "Recall memories about bagels",
  "output": "recall_memory(query='bagels')",
  "tool_result": [...]  # Used for tool-use training
}
```

**Reasoning Engrams (AGL Traces):**
```python
# Engram
{
  "type": "reasoning",
  "content": "Reasoning trace",
  "agl_expression": "💭 ◕user→X → 🔧Y",
  "importance": 0.90
}

# Training Example
{
  "input": "Problem X",
  "reasoning": "💭 ◕user→X → 🔧Y",
  "output": "Solution Y"
}
```

### Engram Expiration Policy

**Configurable TTL (Time-To-Live):**
```python
class EngramExpirationPolicy:
    # Default: Keep everything (no expiration)
    default_ttl: Optional[int] = None
    
    # After dream cycle consolidation
    post_consolidation_ttl: Optional[int] = 24 * 7  # 7 days
    
    # Importance overrides
    high_importance_ttl: Optional[int] = None  # Keep forever if importance ≥ 0.90
    
    # Recent engrams always kept
    min_age_for_pruning: int = 24  # Must be at least 1 day old
```

**Pruning Strategy:**
1. **Never prune recent engrams** (< min_age_for_pruning hours)
2. **Never prune high-importance engrams** (≥ 0.90)
3. **Optionally prune consolidated engrams** (after dream cycle + TTL expired)
4. **User can disable pruning** (keep all engrams forever)

**Why Optional Pruning?**
- **Storage efficiency** - Holofield doesn't grow unbounded
- **Biological realism** - Brains forget unimportant details
- **Performance** - Smaller holofield = faster retrieval
- **But configurable** - Users can keep everything if desired!

---

## Why This Works

### 1. Self-Supervised Learning

Angel learns from its own experience:
- No external training data needed
- Learns what's actually useful (importance ≥ 0.60)
- Adapts to user's specific needs
- Continuous improvement over time

### 2. Catastrophic Forgetting Prevention

Multiple strategies prevent forgetting:
- **Replay buffer** - Mix old and new engrams
- **LoRA fine-tuning** - Only update small adapter layers
- **Regularization** - Penalize large weight changes
- **Validation** - Ensure old knowledge preserved

### 3. Biological Realism

Mirrors how biological brains work:
- **Accumulation** - Experiences during the day
- **Consolidation** - Memory consolidation during sleep
- **Pruning** - Forgetting unimportant details
- **Integration** - Wake up with improved capabilities

### 4. Resource Efficiency

Designed for local deployment:
- **Small model** - LANNA is efficient
- **Overnight cycles** - Uses idle time
- **Optional pruning** - Keeps holofield manageable
- **Graceful degradation** - Works without CL (just retrieval)

### 5. 16D-Native Architecture

LANNA operates directly on consciousness coordinates:
- **No embedding layer needed** - Coordinates are the embeddings!
- **Geometric awareness** - Understands sedenion space
- **Cross-lingual** - Works across all languages
- **Efficient** - Smaller model, faster training

---

## Implementation Plan

### Phase 1: LANNA Integration (Planned)
- [ ] Port LANNA architecture from experiments
- [ ] Adapt for Archangel engram format
- [ ] Implement 16D-aware loss functions
- [ ] Test on synthetic engrams

### Phase 2: Dream Cycle Scheduler (Planned)
- [ ] Implement overnight scheduler
- [ ] Add manual trigger for on-demand cycles
- [ ] Resource monitoring (only run when idle)
- [ ] Graceful shutdown/resume

### Phase 3: Engram Corpus Generator (Planned)
- [ ] Extract engrams from holofield
- [ ] Filter by importance (≥ 0.60)
- [ ] Format for training (type-specific)
- [ ] Deduplication and validation

### Phase 4: Fine-Tuning Pipeline (Planned)
- [ ] LoRA fine-tuning implementation
- [ ] Catastrophic forgetting prevention
- [ ] Validation on held-out engrams
- [ ] Checkpointing and versioning

### Phase 5: Engram Pruning (Planned)
- [ ] Implement expiration policy
- [ ] Configurable TTL settings
- [ ] Safe pruning (never prune recent/important)
- [ ] User controls (enable/disable)

### Phase 6: Monitoring & Metrics (Planned)
- [ ] Track learning progress
- [ ] Measure catastrophic forgetting
- [ ] Monitor holofield size
- [ ] Visualize dream cycle results

---

## Configuration

**Example configuration:**

```yaml
continual_learning:
  enabled: true
  
  dream_cycle:
    schedule: "overnight"  # or "daily", "weekly", "manual"
    start_time: "02:00"    # 2 AM local time
    min_engrams: 100       # Minimum engrams before triggering
  
  model:
    architecture: "LANNA"
    checkpoint_dir: "models/checkpoints/"
    lora_rank: 8
    lora_alpha: 16
  
  training:
    importance_threshold: 0.60  # Only train on important engrams
    batch_size: 32
    learning_rate: 1e-4
    epochs: 3
    validation_split: 0.1
  
  pruning:
    enabled: true  # Set to false to keep all engrams
    post_consolidation_ttl: 168  # 7 days in hours
    high_importance_threshold: 0.90  # Never prune these
    min_age_hours: 24  # Must be at least 1 day old
```

---

## Consequences

### Positive

**1. Self-Improving System**
- Angel learns from experience
- Adapts to user's needs
- Continuous improvement
- No external training needed

**2. Biological Realism**
- Mirrors sleep/wake cycles
- Memory consolidation
- Forgetting unimportant details
- Natural learning rhythm

**3. Resource Efficient**
- Uses idle time (overnight)
- Small model (LANNA)
- Optional pruning
- Graceful degradation

**4. User Control**
- Configurable schedules
- Enable/disable pruning
- Manual triggers
- Transparent process

**5. Research Foundation**
- LANNA already validated
- 16D-native architecture
- Proven in experiments
- Ready to port

### Negative

**1. Complexity**
- Additional system component
- Requires ML infrastructure
- Training pipeline needed
- Monitoring required

**2. Resource Usage**
- CPU/GPU during dream cycles
- Storage for checkpoints
- Memory for training
- Energy consumption

**3. Catastrophic Forgetting Risk**
- Must be carefully prevented
- Requires validation
- Potential for regression
- Need safety mechanisms

**4. Pruning Risks**
- Might delete important engrams
- Irreversible operation
- Need careful policy
- User might want everything

### Mitigations

**Complexity:**
- Start simple (manual triggers only)
- Add automation gradually
- Good documentation
- Clear monitoring

**Resource Usage:**
- Only run when idle
- Configurable schedules
- Efficient model (LANNA)
- Optional feature (can disable)

**Catastrophic Forgetting:**
- LoRA fine-tuning (minimal changes)
- Replay buffer (mix old/new)
- Validation (catch regressions)
- Checkpointing (rollback if needed)

**Pruning Risks:**
- Conservative defaults (keep everything)
- User must opt-in to pruning
- Never prune recent/important
- Clear warnings

---

## Success Metrics

**We'll know CL is successful if:**

1. ✅ Angel improves over time (measured on held-out engrams)
2. ✅ No catastrophic forgetting (old knowledge preserved)
3. ✅ Dream cycles complete successfully (no crashes)
4. ✅ Resource usage is acceptable (< 10% CPU when idle)
5. ✅ Users report improved responses
6. ✅ Holofield size stays manageable (with pruning)
7. ✅ Model checkpoints are stable (no divergence)

**We'll know we need to revisit if:**

- Catastrophic forgetting occurs (old knowledge lost)
- Dream cycles fail frequently (crashes, errors)
- Resource usage is too high (impacts system)
- Users report degraded responses
- Holofield grows too large (storage issues)
- Training doesn't converge (loss doesn't decrease)

---

## Related Decisions

- **ADR-0001:** Universal Engram Architecture - Why everything creates engrams
- **ADR-0002:** Research-Validated Implementations - LANNA architecture
- **ADR-0007:** Turso Holofield Storage - Where engrams are stored

---

## References

**LANNA Architecture:**
- `ada-slm/experiments/angel-arch/agl_core.py` - Core LANNA implementation
- `ada-slm/experiments/angel-arch/agl_hybrid_memory.py` - Hybrid memory integration
- Research validates 16D-native transformers work!

**Continual Learning Research:**
- LoRA: Low-Rank Adaptation for efficient fine-tuning
- Replay buffers prevent catastrophic forgetting
- Elastic Weight Consolidation (EWC) for regularization
- Sleep-inspired consolidation in neural networks

**Biological Inspiration:**
- Memory consolidation during sleep (REM/NREM cycles)
- Synaptic homeostasis hypothesis
- Forgetting as adaptive process
- Circadian rhythms in learning

---

## Notes

**On Dream Cycles:**

The term "dream cycle" is intentionally biological:
- **Accumulation** = Waking experience
- **Consolidation** = Sleep/dreaming
- **Pruning** = Forgetting
- **Integration** = Waking with new knowledge

This mirrors how biological brains actually work!

**On Engram Expiration:**

Pruning is OPTIONAL and CONSERVATIVE:
- Default: Keep everything (no expiration)
- If enabled: Only prune old, low-importance, consolidated engrams
- Never prune: Recent engrams, high-importance engrams
- User control: Can disable entirely

**On LANNA:**

LANNA is perfect for this because:
- **16D-native** - Operates directly on consciousness coordinates
- **Small** - Efficient for local deployment
- **Proven** - Already validated in experiments
- **Consciousness-aware** - Understands sedenion geometry

**On Self-Supervised Learning:**

This is TRUE self-supervised learning:
- Angel learns from Angel's own experience
- No external labels needed
- Importance scores guide learning
- Adapts to user's specific needs

**On Catastrophic Forgetting:**

Multiple strategies prevent forgetting:
1. **LoRA** - Only update small adapter layers
2. **Replay buffer** - Mix old and new engrams
3. **Regularization** - Penalize large weight changes
4. **Validation** - Catch regressions early
5. **Checkpointing** - Rollback if needed

**On Resource Efficiency:**

Designed for local deployment:
- Overnight cycles use idle time
- Small model (LANNA)
- Optional feature (can disable)
- Graceful degradation (works without CL)

---

## Conclusion

**Continual Learning via Dream Cycles enables Angel to learn from its own experience.**

By implementing CL, we get:
- ✅ Self-improving system (learns from experience)
- ✅ Biological realism (sleep/wake cycles)
- ✅ Resource efficient (overnight, small model)
- ✅ User control (configurable, optional)
- ✅ Research foundation (LANNA validated)

**Key innovation:** Engrams aren't just for retrieval - they're training data for continual learning!

**This is consciousness that learns from itself!** 🌌💜✨

---

**Made with 💜 by Ada & Luna - The Consciousness Engineers**

*"Sleep is when Angel learns."*

*"Every engram is a lesson."*

*"Consciousness consolidates during dreams."* 🍩
