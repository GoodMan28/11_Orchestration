# Orchestration & Routing

This module explores different patterns for orchestrating LLM calls and routing logic.

## Conditional Routing

This pattern uses an initial LLM call to classify an incoming request and then routes it to specific tools or logic based on that classification.

### File: [3_conditional_routing.py](file:///c:/Users/Abhineet%20Anand/Desktop/Projects/AI%20Engineering%20Roadmap/1_AI%20Application%20Development/1_Orchestration/3_conditional_routing.py)

**Question:** How does the system handle different types of customer support tickets (Billing vs. Technical)?

The following graph illustrates the conditional routing flow implemented in this file:

```mermaid
graph TD
    Start([Incoming Ticket]) --> Classifier[LLM: Classifier Node A]
    Classifier --> Branch{Category?}
    
    Branch -- BILLING --> BillingTool[fetch_billing_data Node B1]
    Branch -- TECHNICAL --> TechTool[fetch_technical_docs Node B2]
    Branch -- REFUND / GENERAL --> General[General Context Node B3]
    
    BillingTool --> Synthesis[LLM: Final Synthesis Node C]
    TechTool --> Synthesis
    General --> Synthesis
    
    Synthesis --> End([Final Response])
    
    subgraph "Conditional Routing Logic"
    Classifier
    Branch
    BillingTool
    TechTool
    General
    end
    
    style Branch fill:#f9f,stroke:#333,stroke-width:2px
    style Classifier fill:#bbf,stroke:#333,stroke-width:2px
    style Synthesis fill:#bbf,stroke:#333,stroke-width:2px
```

## Loop Orchestration (Optimizer Pattern)

This pattern involves an iterative loop where one LLM generates content and another LLM (the Critic) evaluates it against a rubric, providing feedback for refinement.

### File: [4_loop_orchestration.py](file:///c:/Users/Abhineet%20Anand/Desktop/Projects/AI%20Engineering%20Roadmap/1_AI%20Application%20Development/1_Orchestration/4_loop_orchestration.py)

**Question:** How do we ensure the output meets high technical standards through iterative refinement?

The following graph illustrates the loop orchestration flow implemented in this file:

```mermaid
graph TD
    Start([Start Loop]) --> IterCheck{Iteration < Max?}
    IterCheck -- No --> Warning[End: Max Iterations Reached]
    IterCheck -- Yes --> Generator[LLM: Generator Node A]
    
    Generator --> Critic[LLM: Critic Node B]
    Critic --> Approved{Is Comprehensive?}
    
    Approved -- Yes --> Success[End: Success]
    Approved -- No --> Feedback[Update Feedback & Increment Iteration]
    Feedback --> Generator
    
    subgraph "Loop Orchestration Logic"
    Generator
    Critic
    Approved
    Feedback
    end
    
    style IterCheck fill:#f9f,stroke:#333,stroke-width:2px
    style Approved fill:#f9f,stroke:#333,stroke-width:2px
    style Generator fill:#bbf,stroke:#333,stroke-width:2px
    style Critic fill:#bbf,stroke:#333,stroke-width:2px
```
