import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- 1. Define your standard Python functions ---
# AI ENGINEERING RULE: You MUST include type hints (str) and a docstring. 
# The SDK reads your docstring and sends it to Gemini so it knows what the tool does.

def get_weather(location: str) -> str:
    """Returns the current weather for a specific city."""
    print(f"\n  [System Executing Tool] -> get_weather(location='{location}')")
    
    # In a real app, you would call a real Weather API here. We will mock it.
    if "london" in location.lower():
        return "Heavy rain and windy, 10°C."
    elif "tokyo" in location.lower():
        return "Sunny and clear, 22°C."
    else:
        return "Cloudy, 18°C."

def get_stock_price(ticker: str) -> str:
    """Returns the current stock price for a given stock ticker symbol."""
    print(f"\n  [System Executing Tool] -> get_stock_price(ticker='{ticker}')")
    
    # Mock data
    prices = {"GOOGL": "$175.50", "AAPL": "$190.10", "MSFT": "$420.30"}
    return prices.get(ticker.upper(), "Ticker not found.")

# --- 2. Orchestration ---
if __name__ == "__main__":
    # We use the 'chats' module because it automatically handles the execution loop
    print("Initializing Agent...")
    chat = client.chats.create(
        model="gemini-2.5-flash", 
        config={
            # We simply pass our raw Python functions in a list!
            "tools": [get_weather, get_stock_price] 
        }
    )

    # Let's ask a complex question that requires BOTH tools
    user_prompt = "Should I bring an umbrella to my meeting in London today? Also, how is the GOOGL stock doing?"
    print(f"\nUser: {user_prompt}")
    
    # Send the message
    response = chat.send_message(user_prompt)
    
    # Print the final result
    print(f"\nAgent: {response.text}")


''' Thoery
This is the absolute most important question you can ask right now. You are looking past the "magic" and asking how the engine actually works.

To answer your question directly: **No, the LLM cannot read your Python code, and regular `# comments` are indeed ignored.** What is actually happening is a beautiful combination of Python's internal memory features and the SDK acting as a secret translator. Let's break down exactly how the LLM knows what your tools are, how to use them, and how the execution stops.

---

### 1. How the SDK "Reads" your Function


In Python, a comment starting with `#` is completely ignored by the computer. However, a string wrapped in triple quotes `"""` right under a function definition is called a **Docstring**.

Docstrings are *not* ignored. Python actually saves them in memory as an official attribute of the function called `__doc__`. Furthermore, Python saves your type hints (like `location: str`) in an attribute called `__annotations__`.

When you type `"tools": [get_weather, get_stock_price]`, the Google SDK does this behind the scenes:

1. It looks at your function's name: `get_weather`
2. It grabs the docstring: `"Returns the current weather for a specific city."`
3. It grabs the arguments and type hints: `location`, which is a `string`.

The SDK then automatically builds a **JSON Schema** out of this data and sends it to the Gemini API alongside your prompt. Gemini never sees your Python code; it only sees a JSON manual that says: *"I have a tool called get_weather. It requires a string argument called location. Use it to find the weather."*

### 2. How the LLM "Stops" Execution

LLMs are trained on massive amounts of data, including code and API documentation. Modern models like Gemini are specifically fine-tuned for **Function Calling**.

When the model reads your prompt ("Should I bring an umbrella to my meeting in London?"), it looks at the JSON manual the SDK sent. It realizes: *"I don't know the weather, but the `get_weather` tool does."*

Instead of generating a text response like "I am an AI and don't know the weather," the model generates a special, hidden JSON command that looks like this:

```json
{
  "function_call": {
    "name": "get_weather",
    "args": {
      "location": "London"
    }
  }
}

```

### 3. The Execution Loop (The "Agentic" Part)

This is where the `chat.send_message()` function you used proves its worth. Here is the exact timeline of what happened when you ran your code:

1. **You:** `chat.send_message("Should I bring an umbrella...?")`
2. **SDK:** Sends your text + the JSON Tool Schema to Gemini.
3. **Gemini:** Replies with the `function_call` JSON block shown above.
4. **SDK Interception:** The SDK receives this response, sees it is a `function_call`, and **pauses the conversation**.
5. **Local Execution:** The SDK looks at its local list of Python tools, finds `get_weather`, and literally runs `get_weather(location="London")` on your computer.
6. **SDK Feedback:** The SDK takes the output (`"Heavy rain and windy, 10°C"`) and silently sends a *second* API request back to Gemini that says: *"Here is the tool result: Heavy rain."*
7. **Gemini Final Output:** Gemini reads the result, synthesizes it, and finally outputs the conversational text: *"Yes, bring an umbrella, it's raining in London!"*

### The Big Takeaway

The LLM isn't running your code. It is just outputting formatted JSON asking *you* to run the code. The `google-genai` SDK is just being a very helpful middleman, automatically intercepting the LLM's requests, running the Python functions for you, and handing the answers back to the model.

Does this clear up the magic behind how agents actually work?

If so, we have completely conquered Phase 1! Would you like to move on to **Phase 2: Orchestration & Routing**, where we use an LLM purely as a "brain" to route users to different workflows?

'''