# SYSTEM DESIGN DOCUMENT: ERP HELPDESK AGENTIC AI

## 1. OVERVIEW & PHILOSOPHY
We are building a multi-agent helpdesk system for an ERP platform. 
**Core Principle:** Accuracy over speed. Every response must be verified before reaching the user.
**Architecture:** Plan-Execute-Reflect loop with a mandatory "Devil's Advocate" double-check at the end.

---

## 2. THE COGNITIVE CORE (Model Selection & Cost Optimization)
We use **only OpenAI** models, assigned by cognitive load:

| Agent Role | Model | Rationale |
| :--- | :--- | :--- |
| **Orchestrator (Router)** | `gpt-4o-mini` | Cheap, fast, excellent at classification. Does the heavy routing. |
| **Agent 2 (RAG Expert)** | `gpt-4o` | Needs high reasoning to synthesize documentation and write accurate `.rm` samples. |
| **Agent 3 (Ticket Creator)** | `gpt-4o-mini` | Only needs structured output (JSON). No heavy reasoning required. |
| **Agent 4 (Tool Caller)** | `gpt-4o` | Needs high precision to call APIs and interpret complex ERP data payloads. |
| **Agent 5 (Critic & Synthesizer)** | `gpt-4o` | Must be the smartest model to catch errors and judge correctness. |
| **The Devil's Advocate (Double-Check)** | `gpt-4o` (same as Agent 5, but with a different persona prompt) | Reuses the same instance to save cost, but switches context entirely. |

---

## 3. AGENT CLASSES & RESPONSIBILITIES (Clean Architecture)
Create a separate Python class for each agent. Use Langchain's `BaseTool` and `Runnable` interfaces. 
Store all agents in a `agents/` directory. Use `uv` for dependency management.

### **Agent 1: "Categorizer" (The Router)**
- **Class Name:** `RouterAgent`
- **Input:** Raw user message.
- **Process:** 
  1. Uses `gpt-4o-mini` to classify the message into exactly one of three categories: `SUPPORT`, `ERROR`, or `DATA_CHANGE_REQUEST`.
  2. If confidence is below 85%, asks the user a clarifying question.
- **Output:** A JSON object with the category and the original message.

### **Agent 2: "RAGAgent" (RAG for Support)**
- **Class Name:** `RAGAgent`
- **Vector Store:** ChromaDB (persisted locally).
- **Process:**
  1. Retrieves top-5 relevant ERP documentation chunks.
  2. Generates a step-by-step guide.
  3. If the query asks for a "how-to," it generates a **sample `.rm` file** (a RubyMarkup template for your ERP) as a code block.
- **Output:** A comprehensive support answer.

### **Agent 3: "TicketAgent" (Ticketing Agent)**
- **Class Name:** `TicketAgent`
- **Process:** 
  1. Extracts the user's name from the session context.
  2. Uses `gpt-4o-mini` to generate a 5-word summary.
  3. Assigns a **Severity** based on keywords (e.g., "crash" = 1, "slow" = 3, "how to" = 5).
  4. Generates a sequential Ticket ID (e.g., `ERP-2026-0001`).
- **Output:** A structured ticket JSON. Does *not* send to the user yet.

### **Agent 4: "ToolAgent" (Tool Calling for ERP API)**
- **Class Name:** `ToolAgent`
- **Tools:** Exposes an OpenAPI schema representing your ERP's read-only endpoints (e.g., `/inventory/stock`, `/vendors/recommend`).
- **Process:**
  1. Uses `gpt-4o` with Langchain's built-in `create_openai_tools_agent`.
  2. Calls the ERP API, parses the JSON response.
- **Output:** Raw, structured data from the ERP.

### **Agent 5: "Validator" (The Critic & Synthesizer)**
- **Class Name:** `Validator`
- **Input:** Receives the raw output from Agent 2, 3, or 4.
- **Process:**
  1. **Critique:** Checks if the answer directly answers the user's original question.
  2. **Synthesis:** Formats the raw data into a friendly, human-readable markdown message.
  3. **Double-Check (Devil's Advocate):** **This is the mandatory killer feature.**
     - The agent switches personas: *"You are now a Devil's Advocate. List 3 specific things that could go wrong with this answer (e.g., outdated data, misleading instructions, security risk)."*
     - It then appends a "⚠️ Mitigations" section to the final output proactively warning the user.
- **Output:** The final, verified, double-checked message sent to the UI.

---

## 4. THE ROUTING MATRIX (Agent 1 → Others)

```mermaid
flowchart TD
    User --> Agent1[Agent 1: RouterAgent]
    Agent1 -->|Category: SUPPORT| Agent2[Agent 2: RAGAgent]
    Agent1 -->|Category: ERROR| Agent3[Agent 3: TicketAgent]
    Agent1 -->|Category: DATA_CHANGE_REQUEST| Agent4[Agent 4: ToolAgent]
    Agent2 --> Agent5[Agent 5: Validator]
    Agent3 --> Agent5
    Agent4 --> Agent5
    Agent5 -->|Final Verified Output| UI