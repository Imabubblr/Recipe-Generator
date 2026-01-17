from google import genai
import os

# Initialize client — make sure your API key is set in environment variable GEMINI_API_KEY
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def get_dishes_with_prep(ingredients, style, num_options=3):
    prompt = (
        f"I have the following ingredients: {', '.join(ingredients)}.\n"
        f"Please give me a list of {num_options} {style} dish names you can make with these ingredients, "
        "each with a brief estimated preparation time.\n"
        "Format as a numbered list with dish name and prep time only."
    )
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )
    return response.text

def get_recipe(dish_name, ingredients):
    prompt = (
        f"Provide a detailed recipe for '{dish_name}' using these ingredients: {', '.join(ingredients)}.\n"
        "Include clear step-by-step instructions."
    )
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )
    return response.text

def main():
    print("Welcome to the Recipe Idea Generator!")
    ingredients_input = input("Enter your ingredients separated by commas: ")
    ingredients = [ing.strip() for ing in ingredients_input.split(',')]

    style = input("Enter a recipe style or cuisine (e.g., Italian, Vegan, Quick): ").strip()
    if not style:
        style = "simple"

    # Step 1: Get dishes + prep times
    dishes_text = get_dishes_with_prep(ingredients, style)
    print("\nHere are your dish options with prep times:\n")
    print(dishes_text)

    # Parse the dishes to let the user pick — 
    # We’ll extract dish names by splitting lines and taking the text after the number.
    lines = dishes_text.strip().split('\n')
    dishes = []
    for line in lines:
        # Expect format like: "1. Dish Name (15 min)"
        # We'll extract dish name part by removing number and time
        if '.' in line:
            # Split at first dot and remove prep time in parentheses
            part = line.split('.', 1)[1].strip()
            # Remove prep time in parentheses, if exists
            if '(' in part and ')' in part:
                dish_name = part.split('(')[0].strip()
            else:
                dish_name = part
            dishes.append(dish_name)

    if not dishes:
        print("\nSorry, could not parse dish names. Here's the full list again:\n")
        print(dishes_text)
        return

    # Step 2: User picks one dish
    while True:
        choice = input(f"\nEnter the number (1-{len(dishes)}) of the dish you want the recipe for: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(dishes):
            chosen_dish = dishes[int(choice) - 1]
            break
        else:
            print("Invalid choice, please enter a valid number.")

    # Step 3: Get detailed recipe for chosen dish
    print(f"\nFetching recipe for '{chosen_dish}'...\n")
    recipe = get_recipe(chosen_dish, ingredients)
    print(recipe)

if __name__ == "__main__":
    main()