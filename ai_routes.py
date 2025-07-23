from flask import Blueprint, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
from cache import init_cache, get_cached_response, cache_response

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ai_routes = Blueprint("ai", __name__)
init_cache()

@ai_routes.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_prompt = data.get("prompt", "")
    full_prompt = f"""You are an AI business consultant. A user has this idea: "{user_prompt}".
Give a business strategy including:
1. Value Proposition
2. Market Analysis
3. Target Audience
4. Competitive Risks
5. Next 3 Strategic Steps
"""

    # Check cache first
    cached = get_cached_response(full_prompt)
    if cached:
        return jsonify({"response": cached})

    # Call OpenAI if not cached
    chat_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI business consultant."},
            {"role": "user", "content": full_prompt}
        ]
    )

    response_text = chat_response.choices[0].message.content
    cache_response(full_prompt, response_text)

    return jsonify({"response": response_text})
