# Diagrams

These are the diagrams you'd put in front of a client or in an architecture
review — broader than the in-line ones in [architecture.md](architecture.md).

## 1. Component model (boxes + responsibilities)

```mermaid
flowchart TB
    subgraph User["User surface"]
      T["Microsoft Teams"]
      W["Web chat"]
    end

    subgraph Agent["Agent orchestration"]
      AG["Agent.ask()"]
      CV["Conversation<br/>(multi-turn wrapper)"]
      SE["Sensitivity check<br/>(SENSITIVE tuple)"]
      CG["Confidence gate<br/>(MIN_CONFIDENCE)"]
    end

    subgraph Retrieval["Retrieval"]
      R["TF-IDF Retriever"]
      D[("Sample docs<br/>HR · IT · Security<br/>or SaaS corpus")]
    end

    subgraph Generation["Generation"]
      GEN["complete()"]
      LST["_local_stub<br/>(default)"]
      AZ["Azure OpenAI<br/>adapter"]
      AN["Anthropic<br/>adapter"]
    end

    T --> CV
    W --> CV
    CV --> AG
    AG --> SE
    SE -- "no" --> R
    R --> D
    R --> CG
    CG -- "yes" --> GEN
    GEN --> LST
    GEN -.-> AZ
    GEN -.-> AN
    CG -- "no" --> ESC["Escalation<br/>(human handoff)"]
    SE -- "yes" --> ESC
    GEN --> CV
    ESC --> CV
```

## 2. Sequence — grounded answer with citations

```mermaid
sequenceDiagram
    autonumber
    participant U as User in Teams
    participant C as Conversation
    participant A as Agent.ask()
    participant R as Retriever
    participant G as complete()

    U->>C: "How do I reset my password?"
    C->>A: ask("...") (no context yet)
    A->>A: sensitive? → no
    A->>R: search("how reset password", k=2)
    R-->>A: [it-support.md (0.41), hr-policy.md (0.08)]
    A->>A: top ≥ MIN_CONFIDENCE → yes
    A->>G: complete(query, [it-support.md, hr-policy.md])
    G-->>A: "...portal.example.com [1] ..."
    A-->>C: AgentResponse(escalated=false, sources=[...])
    C->>C: turns.append(turn)
    C-->>U: cited answer + sources
```

## 3. Sequence — sensitive-topic escalation

```mermaid
sequenceDiagram
    autonumber
    participant U as User in Teams
    participant C as Conversation
    participant A as Agent.ask()

    U->>C: "I want a refund on my subscription"
    C->>A: ask("...")
    A->>A: sensitive? → matches "refund"
    A-->>C: AgentResponse(escalated=true, reason="sensitive topic", sources=[])
    Note over A: No retrieval, no generation.<br/>Bypasses the LLM entirely.
    C-->>U: "I'm connecting you with a specialist..."
```

## 4. State — multi-turn conversation context lifecycle

```mermaid
stateDiagram-v2
    [*] --> Fresh: Conversation()
    Fresh --> Turns: ask() (first)
    Turns --> Turns: ask() (next) — bare query confident
    Turns --> ContextInjected: ask() — bare query LOW confidence
    ContextInjected --> Turns: prior turns re-injected as retrieval context
    Turns --> Fresh: reset()
    ContextInjected --> Fresh: reset()
```

The `ContextInjected` transition is the one that makes follow-ups like
"what about for managers?" work — `Conversation.ask()` first tries the
bare query, and only retries with prior-turn context if the first attempt
returned `escalated=true, reason="low confidence"`.

## 5. Decision tree — single turn

```mermaid
flowchart TB
    Q["User question"] --> S{"Matches a SENSITIVE<br/>keyword?"}
    S -- "yes" --> ESC1["Escalate<br/>(sensitive topic)"]
    S -- "no" --> R["Retrieve top-k via TF-IDF"]
    R --> C{"Top score ≥<br/>MIN_CONFIDENCE?"}
    C -- "no" --> ESC2["Escalate<br/>(low confidence)"]
    C -- "yes" --> G["Generate grounded answer<br/>with [n] citations"]
    G --> RET["Return AgentResponse<br/>(escalated=false, sources=[...])"]
    ESC1 --> RETe1["Return AgentResponse<br/>(escalated=true, reason)"]
    ESC2 --> RETe2["Return AgentResponse<br/>(escalated=true, reason)"]
```
