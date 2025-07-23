from flask import Blueprint, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ai_routes = Blueprint("ai", __name__)

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

    chat_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI business consultant."},
            {"role": "user", "content": full_prompt}
        ]
    )

    return jsonify({"response": chat_response.choices[0].message.content})
