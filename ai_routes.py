from flask import Blueprint, request, jsonify, send_file
import openai
import os
import sqlite3
from dotenv import load_dotenv
from cache import init_cache, get_cached_response, cache_response
from io import BytesIO
from fpdf import FPDF

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # API key stored in .env file

ai_routes = Blueprint("ai", __name__)
init_cache()

@ai_routes.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_prompt = data.get("prompt", "")
    session_id = data.get("session_id", None)
    stage = data.get("stage", "")
    industry = data.get("industry", "")
    budget = data.get("budget", "")

    full_prompt = f"""You are an AI business consultant. A user has this idea: \"{user_prompt}\".
Business Stage: {stage}
Industry: {industry}
Budget: ${budget}
Provide a business strategy including:
1. Value Proposition
2. Market Analysis
3. Target Audience
4. Competitive Risks
5. Next 3 Strategic Steps
"""

    cached = get_cached_response(full_prompt, session_id=session_id)
    if cached:
        return jsonify({"response": cached})

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "You are an expert business consultant."},
            {"role": "user", "content": full_prompt}
        ],
        max_tokens=4000,
        temperature=0.7,
        top_p=1
    )

    reply = response.choices[0].message.content.strip()
    cache_response(full_prompt, reply, session_id=session_id)
    return jsonify({"response": reply})


@ai_routes.route("/api/export", methods=["POST"])
def export_response():
    content = request.json.get("content", "")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return send_file(pdf_output, mimetype="application/pdf", as_attachment=True, download_name="business_plan.pdf")
