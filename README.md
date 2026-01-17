# 🍽️ AI Recipe Generator

The AI Recipe Generator is a web-based application designed to assist users in selecting meals based on the ingredients they have available and their preferred cuisine style.

Users input their available ingredients, choose a cuisine category, and the application generates **six AI-powered recipe suggestions**, allowing them to select a recipe that best fits their needs.

---

## ✨ Features

- Ingredient-based recipe generation
- Cuisine selection options
- AI-generated recipes with clear, step-by-step instructions
- Six recipe suggestions generated per request
- Intuitive user interface

---

## 🛠️ Tech Stack

- Python (application logic and AI integration)
- HTML (user interface)
- AI API: OpenRouter (Google Gemini models)
- Environment variables for secure API key management

---

## 🚀 Application Workflow

1. The user enters the ingredients currently available
2. The user selects a preferred cuisine category
3. The application sends the request to the Gemini model
4. The AI generates six distinct recipe suggestions
5. The user selects a recipe to view detailed preparation instructions

---

## 🤖 AI Integration

This application integrates **Google Gemini** models through **OpenRouter’s OpenAI-compatible API**.

- **Model used for recipe generation:**  
  `Google: Gemini 2.5 Pro`

The model interprets ingredient inputs, adapts recipes to the selected cuisine, and generates structured, easy-to-follow instructions.

---

## 🧑‍💻 Running the Project Locally

### Prerequisites

- Python 3.9 or higher
- OpenRouter account

### Setup Instructions

1. Create an OpenRouter account:  
   https://openrouter.ai

2. Generate an API key from the OpenRouter dashboard

3. Set the environment variable:

   ```bash
   export OPENROUTER_API_KEY=sk-or-v1-...

💰 API Costs

This project uses the OpenRouter API, which is a paid service.

Each prompt typically costs a few cents, depending on the selected Gemini model and token usage

Costs may increase with longer prompts or repeated requests

Users are responsible for managing and monitoring their own API usage

For detailed pricing information, refer to OpenRouter’s official pricing documentation.