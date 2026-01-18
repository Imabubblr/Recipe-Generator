from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI
import os
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip('"\'')
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY not set")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

data_store = {}

def get_dishes_with_prep(ingredients, style, mood="", num_options=3):
    mood_line = f"The cook is feeling: {mood}.\n" if mood else ""

    prompt = (
        f"I have these ingredients: {', '.join(ingredients)}.\n"
        f"{mood_line}"
        f"Desired style or cuisine: {style}.\n\n"
        f"Generate {num_options} VERY DISTINCT dish ideas.\n"
        "Each dish must differ clearly in:\n"
        "- cooking method\n"
        "- flavor profile\n"
        "- effort level or vibe\n\n"
        "Mood rules:\n"
        "- tired → fastest, simplest dishes\n"
        "- fancy → elevated, indulgent dishes\n"
        "- comfort → cozy and familiar\n"
        "- craving X → feature X strongly\n\n"
        "Return format (STRICT):\n"
        "1. Dish Name – Prep Time | Emoji"
    )

    response = client.chat.completions.create(
        model="google/gemini-2.5-pro",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9
    )

    return response.choices[0].message.content

def get_recipe(dish_name, ingredients, mood=""):
    mood_line = f"Cook's mood: {mood}. Adjust complexity and tone.\n" if mood else ""

    prompt = (
        f"{mood_line}"
        f"Create a detailed recipe for '{dish_name}' using:\n"
        f"{', '.join(ingredients)}.\n\n"
        "Include step-by-step instructions and helpful tips."
    )

    response = client.chat.completions.create(
        model="google/gemini-2.5-pro",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )

    return response.choices[0].message.content

def parse_dishes(text):
    dishes = []
    for line in text.split("\n"):
        line = line.strip()
        # Match: "1. Dish Name – 15 mins | 😴"
        if re.match(r"^\d+\.\s+", line):
            dishes.append(line.split(".", 1)[1].strip())
    return dishes

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ingredients = [
            i.strip() for i in request.form.get("ingredients", "").split(",")
            if i.strip()
        ]

        style = request.form.get("style", "simple")
        mood = request.form.get("mood", "").strip()

        # NEW: number of options (default 3, clamped 1–12)
        try:
            num_options = int(request.form.get("num_options", 3))
        except ValueError:
            num_options = 3

        num_options = max(1, min(num_options, 12))

        dishes_text = get_dishes_with_prep(
            ingredients,
            style,
            mood,
            num_options=num_options
        )
        dishes = parse_dishes(dishes_text)

        data_store["ingredients"] = ingredients
        data_store["dishes"] = dishes
        data_store["mood"] = mood

        return render_template("dishes.html", dishes=dishes)

    return render_template("index.html")

@app.route("/recipe/<int:dish_index>")
def recipe(dish_index):
    dishes = data_store.get("dishes", [])
    ingredients = data_store.get("ingredients", [])
    mood = data_store.get("mood", "")

    if dish_index < 0 or dish_index >= len(dishes):
        return redirect(url_for("index"))

    dish_name = dishes[dish_index].split("–")[0].strip()
    recipe_text = get_recipe(dish_name, ingredients, mood)

    return render_template(
        "recipe.html",
        dish_name=dish_name,
        recipe=recipe_text
    )

if __name__ == "__main__":
    app.run(debug=True)
