from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_API_KEY = OPENROUTER_API_KEY.strip('"\'') if OPENROUTER_API_KEY else ""

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY or OPENROUTER_API_KEY is not set.\n"
        "Set it in your environment: export OPENROUTER_API_KEY=sk-or-v1-..."
    )

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

def get_dishes_with_prep(ingredients, style, num_options=3):
    prompt = (
        f"I have the following ingredients: {', '.join(ingredients)}.\n"
        f"Please give me a list of {num_options} {style} dish names you can make with these ingredients, "
        "each with a brief estimated preparation time.\n"
        "Format as a numbered list with dish name and prep time only."
    )

    response = client.chat.completions.create(
        model="google/gemini-2.5-pro",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def get_recipe(dish_name, ingredients):
    prompt = (
        f"Provide a detailed recipe for '{dish_name}' using these ingredients: "
        f"{', '.join(ingredients)}.\nInclude clear step-by-step instructions."
    )

    response = client.chat.completions.create(
        model="google/gemini-2.5-pro",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def parse_dishes(dishes_text):
    if not dishes_text:
        return []

    lines = dishes_text.strip().split("\n")
    dishes = []

    for line in lines:
        if "." in line:
            part = line.split(".", 1)[1].strip()
            if " - " in part:
                dish_name = part.split(" - ")[0].strip()
            elif "(" in part:
                dish_name = part.split("(")[0].strip()
            else:
                dish_name = part.strip()
            dishes.append((part, dish_name))
    return dishes

data_store = {}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ingredients_input = request.form.get("ingredients") or ""
        style = (request.form.get("style") or "").strip() or "simple"
        ingredients = [i.strip() for i in ingredients_input.split(",") if i.strip()]

        dishes_text = get_dishes_with_prep(ingredients, style, num_options=6)
        dishes = parse_dishes(dishes_text)

        data_store["ingredients"] = ingredients
        data_store["dishes"] = [dish_name for _, dish_name in dishes]

        dishes_display = [full_text for full_text, _ in dishes]

        return render_template(
            "dishes.html",
            dishes=dishes_display
        )

    return render_template("index.html")

@app.route("/recipe/<int:dish_index>")
def recipe(dish_index):
    ingredients = data_store.get("ingredients")
    dishes = data_store.get("dishes")

    if not ingredients or not dishes or dish_index < 0 or dish_index >= len(dishes):
        return redirect(url_for("index"))

    dish_name = dishes[dish_index]
    recipe_text = get_recipe(dish_name, ingredients)

    return render_template(
        "recipe.html",
        dish_name=dish_name,
        recipe=recipe_text
    )

if __name__ == "__main__":
    app.run(debug=True)
