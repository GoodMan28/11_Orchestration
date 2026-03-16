'''
Here we are implementing a looping orchestrator that:
1. Generates a draft for the topic
2. Evaluates the draft based on the rubric
3. If the draft is good then return it, else return the feedback to the generator to improve the draft
4. Repeat the process until the draft is good or the max iterations are reached
'''

import os
from google import genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. THE CRITIC'S SCHEMA (The Rubric)
# ==========================================

class CritiqueResult(BaseModel):
    is_comprehensive: bool = Field(
        description="True ONLY if the text is highly technical, precise, and sounds like a deep tech researcher."
    )
    feedback: str = Field(
        description="If false, provide bulleted instructions on what is missing or what needs to be deeper."
    )

# ==========================================
# 2. THE NODES
# ==========================================

def generate_draft(topic: str, previous_feedback: str = "") -> str:
    """Node A: The Generator"""
    print("   -> [GENERATOR] Drafting content...")
    prompt = f"Write a highly technical, dense paragraph about {topic}."
    
    if previous_feedback:
        print("   -> [GENERATOR] Applying feedback to new draft...")
        prompt += f"\n\nYou MUST revise your previous attempt based on this feedback:\n{previous_feedback}"
        
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text

def evaluate_draft(draft: str) -> CritiqueResult:
    """Node B: The Critic (Using Structured Output)"""
    print("   -> [CRITIC] Evaluating draft against rubric...")
    prompt = f"Evaluate this draft:\n\n{draft}\n\nIs it rigorous enough for a deep tech paper?"
    
    response = client.models.generate_content(
        model='gemini-3-flash-preview',
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": CritiqueResult,
            "temperature": 0.0 # The critic must be deterministic and cold
        }
    )
    return response.parsed

# ==========================================
# 3. THE ORCHESTRATOR (The Loop)
# ==========================================

def research_agent_loop(topic: str) -> str:
    print(f"\n[STARTING RESEARCH AGENT] Topic: {topic}")
    
    max_iterations = 3 # Safeguard: Never let an LLM loop infinitely
    iteration = 0
    current_feedback = ""
    current_draft = ""
    
    while iteration < max_iterations:
        print(f"\n--- Iteration {iteration + 1} ---")
        
        # Step 1: Generate
        current_draft = generate_draft(topic, current_feedback)
        print(f"Draft Snippet: {current_draft[:100]}...")
        
        # Step 2: Evaluate
        evaluation = evaluate_draft(current_draft)
        
        # Step 3: Conditional Routing based on Evaluation
        if evaluation.is_comprehensive:
            print("\n[SUCCESS] The Critic approved the draft!")
            return current_draft
        else:
            print(f"[REVISION NEEDED] Critic Feedback: {evaluation.feedback}")
            # Update state for the next loop
            current_feedback = evaluation.feedback 
            iteration += 1
            
    print("\n[WARNING] Max iterations reached. Returning the best effort draft.")
    return current_draft

# ==========================================
# 4. EXECUTION
# ==========================================
if __name__ == "__main__":
    final_report = research_agent_loop("protein folding biomarkers for Alzheimer's disease staging")
    print("\n--- FINAL OUTPUT ---")
    print(final_report)