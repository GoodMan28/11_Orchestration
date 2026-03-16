'''
Ticket Resolution using Conditional Routing
Here we will follow the below steps:
1. Define two functions for getting the BILLING_INFO based on the user_id, and the TECHNICAL_INFO based on the ticket_text
2. Then make a "call_llm_structured" that takes the user test, system context and the response format
3. Now we define the "process_ticket function that will use the "call_llm_structured" function to get the classification of the ticket and then based on the classification, it will call the appropriate function to get the system context
4. Finally, we will use the "call_llm_structured" function to get the final response
'''

import json
from enum import Enum
from pydantic import BaseModel, Field
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
# ==========================================
# 1. DEFINE OUR SCHEMAS (The Contracts)
# ==========================================

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class TicketCategory(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    REFUND = "refund"
    GENERAL = "general"

class ClassificationResult(BaseModel):
    category: TicketCategory
    confidence_score: float = Field(description="Confidence from 0.0 to 1.0")

class FinalResponse(BaseModel):
    draft_reply: str
    urgency_score: int = Field(ge=1, le=10, description="1 is low, 10 is critical")
    route_taken: str

# ==========================================
# 2. API WRAPPER (SDK)
# ==========================================

def call_llm_structured(system_prompt: str, user_text: str, response_model: BaseModel) -> BaseModel:
    # This replaces the mock wrapper. This is the only place the LLM is actually invoked.
    print(f"   -> [LLM CALL] Hitting Gemini API with target schema: {response_model.__name__}")
    
    # 2. Make the real API call
    response = client.models.generate_content(
        model='gemini-2.5-flash', # Fast, cheap model perfect for rapid routing
        contents=user_text,
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
            "response_schema": response_model, # We pass your Pydantic class right here
            "temperature": 0.0 # Zero temperature for maximum determinism
        }
    )
    
    # 3. The SDK automatically parses the JSON back into your Pydantic object
    return response.parsed

# ==========================================
# 3. MOCK TOOLS (The Context Gatherers)
# ==========================================

def fetch_billing_data(user_id: str) -> str:
    print("   -> [SYSTEM] Fetching data from Billing Database...")
    return "User has an unpaid invoice of $45.00 from last month."

def fetch_technical_docs(query: str) -> str:
    print("   -> [SYSTEM] Searching Vector Database for Tech Docs...")
    return "Error 404 on the dashboard usually means the cache needs clearing."

# ==========================================
# 4. THE ORCHESTRATOR (The Core Logic)
# Sending the logic to Node A (classifier)
# Then the logic to Node B (tool execution)
# Then the logic to Node C (final synthesis)
# ==========================================

def process_ticket(ticket_text: str, user_id: str) -> str:
    print(f"\n[INCOMING TICKET]: {ticket_text}")
    
    # STEP 1: Route the ticket (Node A)
    classification = call_llm_structured(
        system_prompt="Classify the following customer support ticket.",
        user_text=ticket_text,
        response_model=ClassificationResult
    )
    
    print(f"   <- [ROUTER OUTPUT] Category: {classification.category.value.upper()} (Confidence: {classification.confidence_score})")
    
    # STEP 2 & 3: Conditional Routing & Tool Execution
    system_context = ""
    
    if classification.category == TicketCategory.BILLING:
        system_context = fetch_billing_data(user_id)
    elif classification.category == TicketCategory.TECHNICAL:
        system_context = fetch_technical_docs(ticket_text)
    else:
        system_context = "No specific data found. Provide a polite general response."
        
    # STEP 4: Sequential Chaining to Final Synthesis (Node C)
    synthesis_prompt = (
        f"Write a customer support reply based on this internal data: {system_context}."
    )
    
    final_output = call_llm_structured(
        system_prompt=synthesis_prompt,
        user_text=ticket_text,
        response_model=FinalResponse
    )
    
    final_output.route_taken = classification.category.value
    return final_output.model_dump_json(indent=2)

# ==========================================
# 5. EXECUTION
# ==========================================
if __name__ == "__main__":
    ticket_1 = "Why did I get a charge for $45 on my card?"
    print(process_ticket(ticket_1, user_id="user_883"))
    
    print("-" * 50)
    
    ticket_2 = "My dashboard is throwing an error 404 when I click settings."
    print(process_ticket(ticket_2, user_id="user_883"))