from flask import Blueprint, request, jsonify, send_file
from openai import OpenAI
import os
from dotenv import load_dotenv
from cache import init_cache, get_cached_response, cache_response
from io import BytesIO
from fpdf import FPDF
import requests

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    query = request.args.get("q", "").strip()
    jurisdiction = request.args.get("jurisdiction", "").strip().lower()

    if not query:
        return jsonify({"error": "Missing query"}), 400

    # OpenCorporates API endpoint
    base_url = "https://api.opencorporates.com/v0.4/companies/search"
    params = {
        "q": query,
        "per_page": 10
    }

    if jurisdiction:
        params["jurisdiction_code"] = jurisdiction

    try:
        res = requests.get(base_url, params=params)
        res.raise_for_status()
        results = res.json().get("results", {}).get("companies", [])

        companies = []
        for item in results:
            company = item.get("company", {})
            companies.append({
                "name": company.get("name"),
                "jurisdiction": company.get("jurisdiction_code", "").upper(),
                "status": company.get("current_status", "N/A").capitalize(),
                "company_number": company.get("company_number"),
                "incorporation_date": company.get("incorporation_date"),
                "address": company.get("registered_address_in_full", "N/A"),
                "summary": f"{company.get('name')} is registered in {company.get('jurisdiction_code', '').upper()} and is currently {company.get('current_status', '').lower()}."
            })

        return jsonify(companies)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
