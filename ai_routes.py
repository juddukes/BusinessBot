from flask import Blueprint, request, jsonify
from openai import OpenAI
import os
import sqlite3
from dotenv import load_dotenv
from cache import init_cache, get_cached_response, cache_response

# Load environment variables and initialize OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up Flask blueprint and caching
ai_routes = Blueprint("ai", __name__)
init_cache()

# 🔍 Helper function to get relevant companies from SQLite
def fetch_relevant_companies(prompt):
    keyword = prompt.lower()
    conn = sqlite3.connect("datasets/companies.db")
    c = conn.cursor()
    c.execute("""
        SELECT name, industry, status FROM companies
        WHERE LOWER(name) LIKE ? OR LOWER(industry) LIKE ?
        LIMIT 5
    """, (f"%{keyword}%", f"%{keyword}%"))
    results = c.fetchall()
    conn.close()

    if not results:
        return "No matching companies found."

    context_lines = [f"- {name} ({industry}, status: {status})" for name, industry, status in results]
    return "\n".join(context_lines)

# 🧠 Ask endpoint with RAG-style context
@ai_routes.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_prompt = data.get("prompt", "")

    # Inject relevant company data
    company_context = fetch_relevant_companies(user_prompt)

    full_prompt = f"""You are an AI business consultant. A user has this idea: "{user_prompt}".

Based on the following company data:
{company_context}

Give a business strategy including:
1. Value Proposition
2. Market Analysis
3. Target Audience
4. Competitive Risks
5. Next 3 Strategic Steps
"""

    # Check cache
    cached = get_cached_response(full_prompt)
    if cached:
        return jsonify({"response": cached})

    # Ask OpenAI
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

# 🔎 Company search API for frontend autocomplete or filters
@ai_routes.route("/api/search", methods=["GET"])
def search_companies():
    keyword = request.args.get("q", "").lower()

    conn = sqlite3.connect("datasets/companies.db")
    c = conn.cursor()
    c.execute("""
        SELECT name, industry, status FROM companies
        WHERE LOWER(name) LIKE ? OR LOWER(industry) LIKE ?
        LIMIT 10
    """, (f"%{keyword}%", f"%{keyword}%"))

    results = [{"name": row[0], "industry": row[1], "status": row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(results)
