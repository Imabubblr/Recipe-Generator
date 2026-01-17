from flask import Flask, render_template, request, redirect, url_for
from google import genai
from google.genai.errors import ClientError
import os


app = Flask(__name__)
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def get_dishes_with_prep(ingredients, style, num_options=3):
    prompt = (
        f"I have the following ingredients: {', '.join(ingredients)}.\n"
        f"Please give me a list of {num_options} {style} dish names you can make with these ingredients, "
        "each with a brief estimated preparation time.\n"
        "Format as a numbered list with dish name and prep time only."
    )
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return response.text
    except ClientError:
        return None


def get_recipe(dish_name, ingredients):
    prompt = (
        f"Provide a detailed recipe for '{dish_name}' using these ingredients: {', '.join(ingredients)}.\n"
        "Include clear step-by-step instructions."
    )
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return response.text
    except ClientError:
        return None


def parse_dishes(dishes_text):
    if not dishes_text:
        return []

    lines = dishes_text.strip().split('\n')
    dishes = []
    for line in lines:
        if '.' in line:
            part = line.split('.', 1)[1].strip()
            dish_name = part.split('(')[0].strip()
            dishes.append(dish_name)
    return dishes


# Store data between requests (for demo purposes)
data_store = {}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ingredients_input = request.form.get("ingredients") or ""
        style = (request.form.get("style") or "").strip() or "simple"
        ingredients = [i.strip() for i in ingredients_input.split(",") if i.strip()]

        # ✅ Try/except ensures dishes_text always exists
        try:
            dishes_text = get_dishes_with_prep(ingredients, style)
        except Exception:
            dishes_text = None

        # If API failed, stay on index page and show error
        if not dishes_text:
            return render_template(
                "index.html",
                error="⚠️ AI usage limit reached or an error occurred. Please try again later.",
                retry_after=60  # optional, for countdown
            )

        dishes = parse_dishes(dishes_text)

        # Save for next step
        data_store['ingredients'] = ingredients
        data_store['dishes'] = dishes

        return render_template("dishes.html", dishes=dishes, dishes_text=dishes_text)

    return render_template("index.html")


@app.route("/recipe/<int:dish_index>")
def recipe(dish_index):
    ingredients = data_store.get('ingredients')
    dishes = data_store.get('dishes')

    if not ingredients or not dishes or dish_index < 0 or dish_index >= len(dishes):
        return redirect(url_for('index'))

    dish_name = dishes[dish_index]
    recipe_text = get_recipe(dish_name, ingredients)
    return render_template("recipe.html", dish_name=dish_name, recipe=recipe_text)

if __name__ == "__main__":
    app.run(debug=True)
