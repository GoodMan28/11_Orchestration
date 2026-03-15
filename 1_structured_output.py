from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Ingredient(BaseModel):
    name: str = Field(description="Name of the ingredient.")
    quantity: str = Field(description="Quantity of the ingredient, including units.")

class Recipe(BaseModel):
    recipe_name: str = Field(description="The name of the recipe.")
    prep_time_minutes: Optional[int] = Field(description="Optional time in minutes to prepare the recipe.")
    ingredients: List[Ingredient]
    instructions: List[str]

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = """
Please extract the recipe from the following text.
The user wants to make delicious chocolate chip cookies.
They need 2 and 1/4 cups of all-purpose flour, 1 teaspoon of baking soda,
1 teaspoon of salt, 1 cup of unsalted butter (softened), 3/4 cup of granulated sugar,
3/4 cup of packed brown sugar, 1 teaspoon of vanilla extract, and 2 large eggs.
For the best part, they'll need 2 cups of semisweet chocolate chips.
First, preheat the oven to 375°F (190°C). Then, in a small bowl, whisk together the flour,
baking soda, and salt. In a large bowl, cream together the butter, granulated sugar, and brown sugar
until light and fluffy. Beat in the vanilla and eggs, one at a time. Gradually beat in the dry
ingredients until just combined. Finally, stir in the chocolate chips. Drop by rounded tablespoons
onto ungreased baking sheets and bake for 9 to 11 minutes.
"""

def extract_recipe_data(text: str) -> Recipe:
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=f"Extract the requested data from this recipe step:\n\n{prompt}",
        config={
            "response_mime_type": "application/json",
            # "response_json_schema": Recipe.model_json_schema(), # this is explicit conversion to json
            "response_schema": Recipe, # this is implicit conversion to json
        },
    )
    # implicit conversion to json
    return response.parsed

    # explicit conversion to json
    # recipe = Recipe.model_validate_json(response.text)
    # return recipe


if __name__ == "__main__":
    try:
        # Get the structured data
        print("Extracting recipe data...")
        structured_data = extract_recipe_data(prompt)
        print("Recipe data extracted successfully.")
        
        # Now we can interact with the LLM's output like a normal Python object!

        print(f"Recipe Name: {structured_data.recipe_name}")
        print(f"Prep Time (Minutes): {structured_data.prep_time_minutes}")
        print(f"Ingredients: {str(structured_data.ingredients)}")
        print(f"Instructions: {str(structured_data.instructions)}")
        

        # --- NEW: Save the JSON to a file ---
        output_filename = "1_structured_output.json"
        with open(output_filename, "w") as f:
            # Pydantic's model_dump_json() easily converts the object to a JSON string.
            # indent=4 formats it nicely with line breaks and spaces.
            f.write(structured_data.model_dump_json(indent=4))
            
        print(f"Success! The structured JSON has been saved to '{output_filename}'")

    except Exception as e:
        print(f"An error occurred: {e}")