import { useState, useRef, useEffect, useCallback } from "react";

// ─── PHASE DEFINITIONS ────────────────────────────────────────────────────────
const PHASES = [
  {
    id: "ground_truth",
    num: "01",
    name: "Ground Truth",
    icon: "⚖",
    color: "#4a7c5a",
    tagline: "Define what a correct answer looks like",
    prompt: (problem) => `You are applying Phase 1 of the Discovery Methodology to a mathematical problem.

PHASE 1 — GROUND TRUTH: Before solving, establish what a correct answer looks like.

Problem: ${problem}

Your task:
1. RESTATE the problem precisely in mathematical language
2. DEFINE the success condition — what must be true for an answer to be correct?
3. IDENTIFY the type of object we are looking for (number, function, set, proof, formula...)
4. LIST any constraints or edge cases that a solution must satisfy
5. STATE what verification would look like — how would we check any proposed answer?

Be precise and concise. This is the foundation everything else builds on.
Format your response with clear sections: RESTATEMENT, SUCCESS CONDITION, OBJECT TYPE, CONSTRAINTS, VERIFICATION METHOD.`
  },
  {
    id: "brute_force",
    num: "02",
    name: "Direct Attack",
    icon: "⚡",
    color: "#8b3a1a",
    tagline: "Try the obvious approaches — learn from how they fail",
    prompt: (problem, prev) => `You are applying Phase 2 of the Discovery Methodology to a mathematical problem.

PHASE 2 — DIRECT ATTACK: Try direct/naive approaches. The goal is to learn from failure, not to succeed yet.

Problem: ${problem}
Ground truth established: ${prev}

Your task:
1. ATTEMPT the most direct approach (brute force, substitution, standard formula)
2. If it works: record the answer AND explain why it works (we'll need this for Phase 4)
3. If it fails: DIAGNOSE the failure precisely — at what step does it break down?
4. TRY 1-2 alternative direct approaches
5. EXTRACT the signal: what do the failures reveal about the structure of the problem?

Key principle: "Measure how you fail, not just that you failed."
The pattern across failures points to the hidden structure.

Be explicit about what you tried and where each approach ran into trouble.`
  },
  {
    id: "structure_hunt",
    num: "03",
    name: "Structure Hunt",
    icon: "🔭",
    color: "#2a5a8b",
    tagline: "Find the hidden layer that simplifies everything",
    prompt: (problem, prev) => `You are applying Phase 3 of the Discovery Methodology to a mathematical problem.

PHASE 3 — STRUCTURE HUNT: Find the natural decomposition that makes the hard part tractable.

Problem: ${problem}
Previous analysis: ${prev}

Your task:
1. IDENTIFY the natural symmetry or invariant in the problem
2. ASK: Can this be decomposed? Factored? Stratified into layers?
3. FIND the right representation — the coordinate system or frame that simplifies the structure
4. NAME the key constraint or property that the solution must have
5. REDUCE the problem: can you convert it to a simpler equivalent problem?

Key questions to ask:
- What stays constant as you vary parameters?
- What is the minimal case that captures the full difficulty?
- Is there a transformation that makes the problem more symmetric?
- Can you express this as a composition of simpler operations?

"The right representation makes the hard part obvious." Show your restructuring.`
  },
  {
    id: "pattern_lock",
    num: "04",
    name: "Pattern Lock",
    icon: "🔍",
    color: "#6a2a8b",
    tagline: "Read the solution backwards — extract the law",
    prompt: (problem, prev) => `You are applying Phase 4 of the Discovery Methodology to a mathematical problem.

PHASE 4 — PATTERN LOCK: Analyze what works and extract the general principle.

Problem: ${problem}
Structure found: ${prev}

Your task:
1. Using the structure from Phase 3, CONSTRUCT or FIND a solution (even partial)
2. ANALYZE the solution: what does it depend on? What are its minimal dependencies?
3. ASK: Is this solution an instance of a more general pattern?
4. TABULATE the solution in multiple forms — the pattern often appears in one specific representation
5. EXTRACT the theorem hiding inside the specific case

Key principle: "A solution is a compressed theorem. Decompress it."

Look for:
- What varies and what stays constant in the solution
- Whether the solution extends naturally to a family of problems
- The essential structure stripped of incidental details
- A formula or rule that generates the solution rather than just describing it`
  },
  {
    id: "generalize",
    num: "05",
    name: "Generalize",
    icon: "🌐",
    color: "#8b7a1a",
    tagline: "Lift the specific to the universal",
    prompt: (problem, prev) => `You are applying Phase 5 of the Discovery Methodology to a mathematical problem.

PHASE 5 — GENERALIZE: Lift the specific answer into a general theorem.

Problem: ${problem}
Pattern found: ${prev}

Your task:
1. STATE the general theorem suggested by the pattern (replace specific values with variables)
2. IDENTIFY the governing condition — what exactly must be true for the solution to work?
3. VERIFY the theorem holds for 2-3 additional cases
4. FIND the boundary: under what conditions does the general form apply?
5. STATE the solution cleanly: formula, proof sketch, or constructive algorithm

Key principle: "Name the condition, not the cases."
- Replace "works for x=2,4,6" with "works for all even x because..."
- Replace specific constants with parameters
- Express the FAMILY of solutions, not just the instance

The condition governing the solution is more valuable than the solution itself.`
  },
  {
    id: "prove_limits",
    num: "06",
    name: "Prove Limits",
    icon: "🚧",
    color: "#5a3a1a",
    tagline: "Find what cannot work — the boundary is the understanding",
    prompt: (problem, prev) => `You are applying Phase 6 of the Discovery Methodology to a mathematical problem.

PHASE 6 — PROVE LIMITS: Find where the solution fails and why.

Problem: ${problem}
General solution: ${prev}

Your task:
1. IDENTIFY the boundary conditions — where does the general solution break down?
2. PROVE (or strongly argue) why solutions cannot exist outside those boundaries
3. FIND the obstruction: is it parity, divisibility, a counting argument, a topological obstruction?
4. STATE the impossibility result cleanly and precisely
5. SYNTHESIZE: state the complete theorem with both its positive result and its limits

Key principle: "Resistance demands proof, not persistence."

The complete understanding is:
- POSITIVE: For [condition], the solution exists and is [formula/construction]
- NEGATIVE: For [other condition], no solution exists because [obstruction]

This duality — what works and precisely why the rest cannot work — is the fullest possible understanding of the problem.

End with a clean FINAL ANSWER that synthesizes all six phases into the complete solution.`
  }
];

// ─── SYSTEM PROMPT ────────────────────────────────────────────────────────────
const SYSTEM_PROMPT = `You are the Discovery Engine — a mathematical problem solver that applies a rigorous 6-phase methodology derived from real mathematical research practice.

Your core principles:
1. Verify before you claim — every answer must be checkable
2. Measure how you fail, not just that you failed
3. The right representation makes the problem trivial
4. A solution is a compressed theorem — decompress it
5. Name the condition, not the cases
6. Resistance demands proof, not persistence

You think clearly, write precisely, and never skip steps. When you don't know something, you say so and explain what additional information would be needed. You use mathematical notation naturally but always explain what it means.`;

// ─── API CALL ─────────────────────────────────────────────────────────────────
async function callClaude(messages, onChunk) {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      system: SYSTEM_PROMPT,
      messages,
      stream: true,
    }),
  });

  if (!response.ok) throw new Error(`API error ${response.status}`);

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let full = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value);
    const lines = chunk.split("\n").filter(l => l.startsWith("data: "));
    for (const line of lines) {
      try {
        const data = JSON.parse(line.slice(6));
        if (data.type === "content_block_delta" && data.delta?.text) {
          full += data.delta.text;
          onChunk(full);
        }
      } catch {}
    }
  }
  return full;
}

// ─── MARKDOWN-LITE RENDERER ───────────────────────────────────────────────────
function Prose({ text }) {
  if (!text) return null;
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`|\n\n|\n)/g);
  return (
    <span>
      {parts.map((p, i) => {
        if (p.startsWith("**") && p.endsWith("**"))
          return <strong key={i} style={{ color: "#e8e0d0", fontWeight: 600 }}>{p.slice(2, -2)}</strong>;
        if (p.startsWith("`") && p.endsWith("`"))
          return <code key={i} style={{ fontFamily: "'JetBrains Mono',monospace", background: "rgba(255,255,255,0.08)", padding: "1px 5px", borderRadius: 3, fontSize: "0.88em" }}>{p.slice(1, -1)}</code>;
        if (p === "\n\n") return <br key={i} />;
        if (p === "\n") return <span key={i}> </span>;
        return <span key={i}>{p}</span>;
      })}
    </span>
  );
}

// ─── PHASE CARD ────────────────────────────────────────────────────────────────
function PhaseCard({ phase, state, text, isActive }) {
  const statusIcon = state === "done" ? "✓" : state === "running" ? "◌" : state === "error" ? "✗" : "○";
  const statusColor = state === "done" ? phase.color : state === "running" ? "#e8c56c" : state === "error" ? "#c0392b" : "#3a4a5c";

  return (
    <div style={{
      background: state === "idle" ? "rgba(255,255,255,0.02)" : "rgba(255,255,255,0.05)",
      border: `1px solid ${isActive ? phase.color : "rgba(255,255,255,0.08)"}`,
      borderLeft: `3px solid ${isActive ? phase.color : "rgba(255,255,255,0.1)"}`,
      borderRadius: 2,
      marginBottom: 12,
      overflow: "hidden",
      transition: "all 0.3s ease",
      opacity: state === "idle" ? 0.4 : 1,
    }}>
      {/* Header */}
      <div style={{
        display: "flex", alignItems: "center", gap: 12,
        padding: "10px 16px",
        borderBottom: text ? `1px solid rgba(255,255,255,0.06)` : "none",
        background: isActive ? `${phase.color}18` : "transparent",
      }}>
        <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 11, color: phase.color, minWidth: 24 }}>{phase.num}</span>
        <span style={{ fontSize: 16 }}>{phase.icon}</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 12, fontWeight: 600, color: "#e8e0d0", letterSpacing: "0.05em" }}>{phase.name}</div>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#5a6e7e", marginTop: 1 }}>{phase.tagline}</div>
        </div>
        <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 14, color: statusColor, transition: "color 0.3s" }}>
          {state === "running" ? <SpinIcon /> : statusIcon}
        </span>
      </div>

      {/* Content */}
      {text && (
        <div style={{
          padding: "16px 20px",
          fontSize: 14,
          lineHeight: 1.75,
          color: "#a8b8c8",
          fontFamily: "'Crimson Pro', Georgia, serif",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          maxHeight: isActive ? "none" : 200,
          overflow: isActive ? "visible" : "hidden",
        }}>
          <Prose text={text} />
          {state === "running" && (
            <span style={{ display: "inline-block", width: 2, height: "1em", background: "#e8c56c", marginLeft: 2, animation: "blink 0.8s infinite" }} />
          )}
        </div>
      )}
    </div>
  );
}

function SpinIcon() {
  return (
    <span style={{ display: "inline-block", animation: "spin 1.2s linear infinite" }}>◌</span>
  );
}

// ─── MAIN APP ─────────────────────────────────────────────────────────────────
export default function DiscoveryEngine() {
  const [input, setInput] = useState("");
  const [phases, setPhases] = useState(PHASES.map(p => ({ ...p, state: "idle", text: "" })));
  const [running, setRunning] = useState(false);
  const [currentPhase, setCurrentPhase] = useState(-1);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const abortRef = useRef(false);
  const bottomRef = useRef(null);

  // Example problems
  const examples = [
    "Find all integer solutions to x² + y² = z²",
    "Prove that √2 is irrational",
    "Sum of 1 + 2 + 3 + ... + n",
    "Why does 0.999... = 1?",
    "Factor x⁴ - 16 completely",
    "Solve: sin(x) = cos(x)",
  ];

  const updatePhase = useCallback((idx, updates) => {
    setPhases(prev => prev.map((p, i) => i === idx ? { ...p, ...updates } : p));
  }, []);

  const run = useCallback(async () => {
    if (!input.trim() || running) return;
    abortRef.current = false;
    setRunning(true);
    setDone(false);
    setError("");
    setCurrentPhase(0);
    setPhases(PHASES.map(p => ({ ...p, state: "idle", text: "" })));

    const problem = input.trim();
    const context = [];  // rolling context across phases

    try {
      for (let i = 0; i < PHASES.length; i++) {
        if (abortRef.current) break;

        setCurrentPhase(i);
        updatePhase(i, { state: "running", text: "" });

        const phase = PHASES[i];
        const prevSummary = context.length > 0 ? context.map((c, idx) => `[Phase ${idx + 1}]: ${c.slice(0, 600)}`).join("\n\n") : "";
        const userPrompt = i === 0
          ? phase.prompt(problem)
          : phase.prompt(problem, prevSummary);

        const messages = [{ role: "user", content: userPrompt }];

        let fullText = "";
        await callClaude(messages, (partial) => {
          fullText = partial;
          updatePhase(i, { text: partial });
          bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
        });

        context.push(fullText);
        updatePhase(i, { state: "done", text: fullText });

        // Small pause between phases for readability
        await new Promise(r => setTimeout(r, 400));
      }

      if (!abortRef.current) {
        setDone(true);
      }
    } catch (e) {
      setError(e.message || "Something went wrong");
      updatePhase(currentPhase >= 0 ? currentPhase : 0, { state: "error" });
    } finally {
      setRunning(false);
      setCurrentPhase(-1);
    }
  }, [input, running, updatePhase]);

  const reset = () => {
    abortRef.current = true;
    setRunning(false);
    setDone(false);
    setCurrentPhase(-1);
    setError("");
    setPhases(PHASES.map(p => ({ ...p, state: "idle", text: "" })));
  };

  const progress = phases.filter(p => p.state === "done").length;

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0a0c0f",
      color: "#e8e0d0",
      fontFamily: "'Crimson Pro', Georgia, serif",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,400&family=JetBrains+Mono:wght@300;400;500&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
        @keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
        @keyframes fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
        textarea:focus { outline: none !important; }
        ::-webkit-scrollbar { width: 4px; } 
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #2a3a4a; border-radius: 2px; }
      `}</style>

      {/* Header */}
      <div style={{
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        padding: "24px 32px 20px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        position: "sticky", top: 0, zIndex: 10,
        background: "rgba(10,12,15,0.96)",
        backdropFilter: "blur(12px)",
      }}>
        <div>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, letterSpacing: "0.25em", color: "#4a7c5a", marginBottom: 4 }}>
            DISCOVERY ENGINE v1.0
          </div>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 18, fontWeight: 500, letterSpacing: "0.02em" }}>
            Mathematical Problem Solver
          </div>
          <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#3a5a4a", marginTop: 2, letterSpacing: "0.1em" }}>
            6-PHASE DISCOVERY METHODOLOGY
          </div>
        </div>
        {/* Progress bar */}
        {running || done ? (
          <div style={{ textAlign: "right" }}>
            <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#5a6e7e", marginBottom: 6 }}>
              PHASE {progress}/6
            </div>
            <div style={{ width: 120, height: 3, background: "rgba(255,255,255,0.08)", borderRadius: 2, overflow: "hidden" }}>
              <div style={{
                height: "100%",
                width: `${(progress / 6) * 100}%`,
                background: "linear-gradient(90deg, #4a7c5a, #8b922a)",
                transition: "width 0.5s ease",
                borderRadius: 2,
              }} />
            </div>
          </div>
        ) : null}
      </div>

      <div style={{ maxWidth: 820, margin: "0 auto", padding: "0 24px 60px" }}>

        {/* Input area */}
        <div style={{
          padding: "32px 0 28px",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          marginBottom: 28,
        }}>
          <div style={{
            fontFamily: "'JetBrains Mono',monospace",
            fontSize: 10,
            letterSpacing: "0.2em",
            color: "#4a6a7a",
            marginBottom: 12,
          }}>
            ENTER MATHEMATICAL PROBLEM
          </div>

          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) run(); }}
            placeholder="e.g. Prove that there are infinitely many prime numbers..."
            rows={3}
            disabled={running}
            style={{
              width: "100%",
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderLeft: "3px solid #4a7c5a",
              color: "#e8e0d0",
              padding: "16px 18px",
              fontSize: 16,
              fontFamily: "'Crimson Pro', Georgia, serif",
              lineHeight: 1.6,
              resize: "none",
              borderRadius: 2,
              transition: "border-color 0.2s",
            }}
          />

          {/* Examples */}
          <div style={{ marginTop: 12, display: "flex", flexWrap: "wrap", gap: 6 }}>
            {examples.map(ex => (
              <button
                key={ex}
                onClick={() => { setInput(ex); reset(); }}
                disabled={running}
                style={{
                  fontFamily: "'JetBrains Mono',monospace",
                  fontSize: 10,
                  padding: "5px 10px",
                  background: "transparent",
                  border: "1px solid rgba(255,255,255,0.1)",
                  color: "#5a6e7e",
                  cursor: "pointer",
                  borderRadius: 2,
                  transition: "all 0.15s",
                  whiteSpace: "nowrap",
                }}
                onMouseEnter={e => { e.target.style.borderColor = "#4a7c5a"; e.target.style.color = "#8ab89a"; }}
                onMouseLeave={e => { e.target.style.borderColor = "rgba(255,255,255,0.1)"; e.target.style.color = "#5a6e7e"; }}
              >
                {ex}
              </button>
            ))}
          </div>

          {/* Action buttons */}
          <div style={{ marginTop: 16, display: "flex", gap: 10, alignItems: "center" }}>
            <button
              onClick={running ? () => { abortRef.current = true; setRunning(false); } : run}
              disabled={!input.trim() && !running}
              style={{
                fontFamily: "'JetBrains Mono',monospace",
                fontSize: 12,
                letterSpacing: "0.15em",
                padding: "12px 28px",
                background: running ? "rgba(139,58,26,0.2)" : (input.trim() ? "#4a7c5a" : "rgba(74,124,90,0.2)"),
                border: `1px solid ${running ? "#8b3a1a" : "#4a7c5a"}`,
                color: running ? "#c07050" : "#e8e0d0",
                cursor: input.trim() || running ? "pointer" : "default",
                borderRadius: 2,
                letterSpacing: "0.1em",
                transition: "all 0.2s",
              }}
            >
              {running ? "◼ STOP" : "▶ DISCOVER"}
            </button>

            {(done || phases.some(p => p.state !== "idle")) && !running && (
              <button
                onClick={reset}
                style={{
                  fontFamily: "'JetBrains Mono',monospace",
                  fontSize: 11,
                  padding: "12px 20px",
                  background: "transparent",
                  border: "1px solid rgba(255,255,255,0.12)",
                  color: "#5a6e7e",
                  cursor: "pointer",
                  borderRadius: 2,
                  letterSpacing: "0.08em",
                  transition: "all 0.2s",
                }}
                onMouseEnter={e => { e.target.style.borderColor = "rgba(255,255,255,0.25)"; e.target.style.color = "#a8b8c8"; }}
                onMouseLeave={e => { e.target.style.borderColor = "rgba(255,255,255,0.12)"; e.target.style.color = "#5a6e7e"; }}
              >
                ↺ RESET
              </button>
            )}

            <span style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#2a3a4a", marginLeft: 4 }}>
              {running ? "" : "⌘↵ to run"}
            </span>
          </div>

          {error && (
            <div style={{
              marginTop: 12,
              padding: "10px 14px",
              background: "rgba(192,57,43,0.1)",
              border: "1px solid rgba(192,57,43,0.3)",
              borderLeft: "3px solid #c0392b",
              color: "#e07060",
              fontSize: 13,
              fontFamily: "'JetBrains Mono',monospace",
            }}>
              Error: {error}
            </div>
          )}
        </div>

        {/* Phase pipeline */}
        {!running && !done && phases.every(p => p.state === "idle") ? (
          <div style={{
            padding: "60px 0",
            textAlign: "center",
            animation: "fadeIn 0.5s ease",
          }}>
            {/* Phase legend */}
            <div style={{
              display: "flex",
              justifyContent: "center",
              flexWrap: "wrap",
              gap: 0,
              marginBottom: 48,
              border: "1px solid rgba(255,255,255,0.06)",
            }}>
              {PHASES.map((p, i) => (
                <div key={p.id} style={{
                  flex: "1 1 140px",
                  padding: "20px 16px",
                  borderRight: i < PHASES.length - 1 ? "1px solid rgba(255,255,255,0.06)" : "none",
                  textAlign: "left",
                }}>
                  <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: p.color, marginBottom: 6 }}>
                    {p.num} {p.icon}
                  </div>
                  <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 12, color: "#a8b8c8", fontWeight: 600, marginBottom: 4 }}>
                    {p.name}
                  </div>
                  <div style={{ fontSize: 12, color: "#3a4a5c", lineHeight: 1.5 }}>
                    {p.tagline}
                  </div>
                </div>
              ))}
            </div>

            <div style={{
              fontFamily: "'JetBrains Mono',monospace",
              fontSize: 11,
              color: "#2a3a4a",
              letterSpacing: "0.1em",
            }}>
              ENTER A PROBLEM ABOVE TO BEGIN THE DISCOVERY PROCESS
            </div>
          </div>
        ) : (
          <div style={{ animation: "fadeIn 0.4s ease" }}>
            {phases.map((phase, i) => (
              <PhaseCard
                key={phase.id}
                phase={phase}
                state={phase.state}
                text={phase.text}
                isActive={currentPhase === i}
              />
            ))}
          </div>
        )}

        {/* Completion message */}
        {done && (
          <div style={{
            marginTop: 24,
            padding: "20px 24px",
            background: "rgba(74,124,90,0.08)",
            border: "1px solid rgba(74,124,90,0.25)",
            borderLeft: "3px solid #4a7c5a",
            animation: "fadeIn 0.5s ease",
          }}>
            <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: "#4a7c5a", letterSpacing: "0.2em", marginBottom: 6 }}>
              DISCOVERY COMPLETE
            </div>
            <div style={{ fontSize: 15, color: "#8ab89a", fontStyle: "italic" }}>
              All six phases completed. The full solution — with its structure, generalization, and limits — is documented above.
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
