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
