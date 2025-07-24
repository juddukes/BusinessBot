from flask import Blueprint, request, jsonify
from openai import OpenAI
import os
import sqlite3
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
    session_id = data.get("session_id", None)

    full_prompt = f"""You are an AI business consultant. A user has this idea: "{user_prompt}".
Give a business strategy including:
1. Value Proposition
2. Market Analysis
3. Target Audience
4. Competitive Risks
5. Next 3 Strategic Steps
"""

    cached = get_cached_response(full_prompt, session_id=session_id)
    if cached:
        return jsonify({"response": cached})

    chat_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI business consultant."},
            {"role": "user", "content": full_prompt}
        ]
    )

    response_text = chat_response.choices[0].message.content
    cache_response(full_prompt, response_text, session_id=session_id)

    return jsonify({"response": response_text})


@ai_routes.route("/api/search", methods=["GET"])
def search_companies():
    keyword = request.args.get("q", "").lower()
    status = request.args.get("status", "").lower()
    jurisdiction = request.args.get("jurisdiction", "").lower()

    conn = sqlite3.connect("datasets/companies.db")
    c = conn.cursor()

    query = """
        SELECT name, industry, status, jurisdiction FROM companies
        WHERE (LOWER(name) LIKE ? OR LOWER(industry) LIKE ?)
    """
    params = [f"%{keyword}%", f"%{keyword}%"]

    if status:
        query += " AND LOWER(status) = ?"
        params.append(status)

    if jurisdiction:
        query += " AND LOWER(jurisdiction) = ?"
        params.append(jurisdiction)

    query += " LIMIT 20"

    c.execute(query, params)
    results = [{"name": row[0], "industry": row[1], "status": row[2], "jurisdiction": row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(results)
