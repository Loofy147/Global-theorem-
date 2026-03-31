# Phase 8: Closed-Loop Sovereign Autonomy — Implementation Checklist

## 1. Infrastructure (Foundational Resilience)
- [x] Create `requirements.txt` for consistent environment setup.
- [ ] Implement `research/tests/test_knowledge_mapper.py`.
- [ ] Implement `research/tests/test_tlm.py`.
- [ ] Implement `research/tests/test_agentic_bridge.py`.
- [ ] Implement `research/tests/test_action_mapper.py`.

## 2. Refinement (Semantic Grounding)
- [x] **FIXME**: Replace MD5 hashing in `ActionMapper.resolve_intent` with TLM-based coordinate lifting.
- [ ] **TODO**: Implement dynamic $m$ resizing in `TGIAgent` based on `HardwareMapper` telemetry.
- [x] **TODO**: Add docstrings to `algebraic.py` and `aimo_3_gateway.py` to reduce documentation debt.

## 3. Execution (Agentic Completion)
- [ ] **TODO**: Build the `ActionExecutor` class in `research/agentic_action_engine.py` to handle real MCP tool calls.
- [ ] **TODO**: Implement the feedback loop where tool results are re-ingested into the TGI ontology.

## 4. Resilience (Codex Enforcement)
- [ ] **TODO**: Add Law-based guardrails to `AgenticBridge` to prevent "Topological Drift".
- [ ] **TODO**: Implement automated $H^2$ parity recovery in the `ActionExecutor`.

---
*Last Updated: March 2026 — Implementation in Progress*
