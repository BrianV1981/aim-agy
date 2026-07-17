# A.I.M. (Actual Intelligent Memory)

A.I.M. is an open-source engineering exoskeleton designed to solve context amnesia, token bloat, state loss, and drift in long-running autonomous AI coding sessions. 

It wraps around CLI agents (primarily Google's Antigravity CLI) and provides a full operating system for your AI, forcing it to act like a disciplined Principal Engineer.

## 🚀 Quickstart & Installation

A.I.M. requires **Linux** or **WSL (Ubuntu)**, Node.js v20+, and aim-opencode.

A.I.M. provides two completely self-contained, isolated installation paths depending on your goal. Both paths install a localized copy of the OS engine directly into your folder.

### Option A: The Clean Exoskeleton (Recommended)
Use this if you want to wrap A.I.M. around your own unique coding project. It installs the engine, severs the Git connection, and deletes the developer artifacts (like tests and benchmarks) to give you a clean, lightweight shell.

```bash
curl -fsSL https://raw.githubusercontent.com/BrianV1981/aim-agy/main/aim-agy_os/install-clean.sh | bash
```

### Option B: The Core Contributor
Use this if you intend to hack on the core A.I.M. framework itself. It preserves the GitHub connection and all internal testing folders.

```bash
curl -fsSL https://raw.githubusercontent.com/BrianV1981/aim-agy/main/aim-agy_os/install-core.sh | bash
```

### Option C: The Sovereign Co-Agent
Use this to spin up a completely independent, headless A.I.M. Co-Agent. It creates a dedicated OS, downloads a specific persona blueprint from the `aim-coagents` DNA Bank, and links it to a Chalkboard for autonomous background work without interfering with your main project's database.

```bash
# Example: Spawns a sovereign Python Developer node
curl -fsSL https://raw.githubusercontent.com/BrianV1981/aim-agy/main/aim-agy_os/install-agent.sh | bash -s python-developer
```

### 2. The Agentic Interview
After installation, reload your shell (`source ~/.bashrc`). Your A.I.M. agent will be fully functional with default settings. 

If you want to customize your agent, execute `aim init`. 
The A.I.M. Onboarding Architect will wake up and conduct a conversational interview to dynamically generate your identity and configuration files.

### 3. Configure Your AI Providers
Launch the interactive dashboard to set your API keys, local Ollama models, and configure the background Wiki daemon.
```bash
aim tui
```


---

## 🔥 Core Capabilities

A.I.M. provides a massive suite of tools to control, manage, and scale your AI agents:

*   **Embedded LanceDB Memory (RAG 5.21):** Replaces standard sliding-window context with a high-fidelity, columnar vector database featuring Native Hybrid Search (Ollama semantics + Tantivy FTS) and an Entity Intersection Reranker.
*   **Background Markdown Generation:** A deterministic Python script strips terminal noise, reducing context weight by 85%. A background daemon then weaves this into a human-readable Markdown wiki (`memory-wiki/`).
*   **GitOps Enforcement:** AI agents are forbidden from coding on `main`. They must create GitHub issues (`aim bug`), branch out into isolated worktrees (`aim fix`), use TDD, and deploy atomically (`aim push`).
*   **Interactive TUI Cockpit:** A visual terminal interface (`aim tui`) to configure LLM routing, guardrails, and context limits without editing JSON files.
*   **Cognitive Routing:** Route expensive coding tasks to flagship models (e.g., Antigravity Pro) in your terminal, while offloading repetitive background tasks (like memory indexing) to free, local models (e.g., Ollama) on your GPU.
*   **P2P Knowledge Cartridges:** Package thousands of pages of documentation into pre-vectorized Native Apache Arrow `.parquet` files. Share and download them peer-to-peer via BitTorrent (`aim export` / `aim jack-in`) to give agents instant recall of entire frameworks without burning API tokens.
*   **Universal IDE Support (MCP):** A built-in FastMCP server exposes the memory databases to any connected IDE (Cursor, VS Code, Claude Desktop) without requiring platform-specific adapters.
*   **Crash Recovery & Handoffs:** When the context window fills up, run `aim reincarnate` to extract active context and spawn a fresh terminal session. If the CLI crashes, run `aim crash` to salvage the interrupted session.
*   **Anti-Drift Shield:** A background hook continuously tracks autonomous tool calls. Every 50 actions, it forcefully halts execution and requires the agent to recite its GitOps rules, preventing "Lost in the Middle" context degradation.
*   **Peer-to-Peer Wiki Sync (Syncthing):** Offload heavy memory compilation to a secondary server by syncing the `memory-wiki/` folder natively via Syncthing.

---

## 🏆 State-of-the-Art Benchmarks (LongMemEval)

A.I.M. uses a custom-built **RAG 5.21 Memory Engine** powered by an embedded LanceDB vector database and a local Ollama instance (running `nomic-embed-text`). This engine cures the "Entity Blindness" of standard vector retrieval by utilizing an `EntityIntersectionReranker` that actively multiplies proper-noun semantic scores by 1.5x and retrieves chronological "Sandwich Contexts" to prevent temporal amnesia.

On the rigorous academic **LongMemEval** benchmark (19,195 complex conversation histories, ICLR 2025), commercial enterprise systems typically score between 82% and 94% on end-to-end recall.

The open-source, locally hosted A.I.M. RAG 5.21 architecture achieves a mathematically verified **95.6% Recall@5** and a staggering **88.2% Recall@1** score on LongMemEval—competing with and effectively beating the state-of-the-art leaderboard. 

*(A fully transparent, immutable JSON proof log mapping the exact Tantivy FTS scores and retrievals for all 500 questions is available in our [locomo-v2 benchmark repository](https://github.com/BrianV1981/locomo-v2/tree/main/benchmark_toolkit)).*

---

## 📖 Documentation & Philosophy

A.I.M. separates fast onboarding documentation from deep philosophical essays and architectural diagrams.

- **[The Official A.I.M. Wiki](https://github.com/BrianV1981/aim/wiki)**: The primary onboarding ramp. Includes step-by-step user guides, configuration variables, and tutorials.
- **[The A.I.M. Knowledge Base (Public Obsidian Vault)](https://github.com/BrianV1981/aim-wiki)**: A massive, decentralized digital garden containing our raw benchmark JSON logs, architectural design history, and the complete "vibe coding" origin story.

---

<!-- AIM_ECOSYSTEM_START -->
### 🧬 The A.I.M. Ecosystem

Modular A.I.M. (Actual Intelligent Memory) repositories. **Flagship engine: [aim-agy](https://github.com/BrianV1981/aim-agy).**

**Active vessels (CLI hosts):**
- **[aim-agy](https://github.com/BrianV1981/aim-agy)** — Core engine / *soul* (Antigravity CLI). *Flagship.* Shared nested `aim-agy_os/` ships here first.
- **[aim-grok](https://github.com/BrianV1981/aim-grok)** — Grok CLI vessel (hybrid memory, GitOps, wiki, fleet orchestration tooling).
- **[aim-opencode](https://github.com/BrianV1981/aim-opencode)** — OpenCode CLI vessel.
- **[aim-codex](https://github.com/BrianV1981/aim-codex)** — OpenAI Codex CLI vessel (greenfield nested soul + Codex overlays; primary `main`).

**Tools & workspaces:**
- **[aim-connect](https://github.com/BrianV1981/aim-connect)** — Self-hosted remote workspace web UI.
- **[aim-tmux-dashboard](https://github.com/BrianV1981/aim-tmux-dashboard)** — Terminal multi-session monitor.
- **[aim-browser](https://github.com/BrianV1981/aim-browser)** — Headed Chromium CDP engine + browser **skill suite**.
- **[aim-google](https://github.com/BrianV1981/aim-google)** — Google Workspace CLI (Gmail, Drive, Calendar, …).
- **[aim-flight-recorder](https://github.com/BrianV1981/aim-flight-recorder)** — Forensic Markdown session extractor.
- **[aim-boardroom](https://github.com/BrianV1981/aim-boardroom)** — Multi-agent orchestration room (OS multiplexing + artifacts).
- **[aim-skills](https://github.com/BrianV1981/aim-skills)** — **Skills index / multi-CLI install registry** (agy, grok, opencode, codex).

**DNA, comms & lore:**
- **[aim-coagents](https://github.com/BrianV1981/aim-coagents)** — DNA bank for sovereign co-agent blueprints.
- **[aim-knowledge](https://github.com/BrianV1981/aim-knowledge)** — Public Obsidian vault / deep-lore archive.
- **[aim-chalkboard](https://github.com/BrianV1981/aim-chalkboard)** — Optional cross-host async git mailbox (PoC; default same-host comms = **aim-communicate** skill).

**Deprecated / not maintained:**
- **[aim](https://github.com/BrianV1981/aim)** — Original **Gemini CLI** framework. Deprecated after loss of practical subscription access; **Great Migration → aim-agy**.
- **[aim-swarm](https://github.com/BrianV1981/aim-swarm)** — Legacy Python swarm factory → use **aim-coagents** + aim-agy spawn.
- **aim-claude / Anthropic-line vessels** — **Done.** Operator does not develop against Anthropic. Use **aim-agy / aim-grok / aim-opencode / aim-codex**.

Full map: see **aim-skills** `docs/AIM_ECOSYSTEM_MAP.md` or Operator artifact `AIM_ECOSYSTEM_MAP.md`.
<!-- AIM_ECOSYSTEM_END -->

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
☕ **Support the project:** [Buy Me a Coffee](https://buymeacoffee.com/brianv1981)