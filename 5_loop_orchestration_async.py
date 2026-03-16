'''
https://youtu.be/Qb9s3UiMSTA?si=zwMG6bHblKRPh0hI refer for the asyncio
https://github.com/GoodMan28/JavaScript-Introduction-main-main/blob/main/.devcontainer/01_basics/week2/JSArchitecture.js see the architecture for better understanding
'''
import dotenv
from google import genai
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==========================================
# 1. THE ASYNC WORKER NODE
# ==========================================

async def get_perspective(perspective: str, topic: str) -> str: 
    # it hits the gemini API and gets the result
    print(f"   -> [LAUNCHING] the perspective of a {perspective} ...")
    prompt = f"Analyze '{topic}' strictly from the perspective of a {perspective}. Keep it to one short, insightful paragraph."
    response = await client.aio.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    print(f"   <- [COMPLETED] Received perspective: {perspective}")
    return f"### {perspective.upper()} PERSPECTIVE\n{response.text}\n"



# ==========================================
# 2. THE ORCHESTRATOR (The Parallel Graph)
# ==========================================

async def parallel_research_agent(topic: str) -> str:
    print(f"\n[STARTING PARALLEL RESEARCH] Topic: {topic}\n")
    
    # tasks help us perform the job concurrently
    tasks = [
        get_perspective("Behavioral Economist", topic),
        get_perspective("Gen Z and Gen Alpha Trend Analyst", topic),
        get_perspective("Fintech Regulatory Expert", topic),
    ]

    # the above coroutines does not run until we are running them by gathering or individually calling them
    result = await asyncio.gather(*tasks)

    print("\n[AGGREGATING RESULTS] Synthesizing final report...\n")

    aggregated_context = "\n".join(result)
    synthesis_prompt = (
        f"Synthesize these diverse expert perspectives into a single executive summary "
        f"on {topic}:\n\n{aggregated_context}"
    )

    final_response = await client.aio.models.generate_content(
        model='gemini-3-flash-preview', 
        contents=synthesis_prompt
    )
    
    return final_response.text


# ==========================================
# 3. THE MAIN FUNCTION
# ==========================================

if __name__ == "__main__":
    # A complex topic that benefits from parallel research
    target_topic = "Designing a new fintech product to address Gen Alpha's unique financial challenges"
    
    # asyncio.run() is the standard Python method to execute a top-level async function
    final_report = asyncio.run(parallel_research_agent(target_topic))
    
    print("\n--- EXECUTIVE SUMMARY ---")
    print(final_report)