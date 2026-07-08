from flask import Flask, request, jsonify
import os
import json
import urllib.request
import re

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE = "https://openrouter.ai/api/v1"
MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")

SYSTEM_PROMPT = """You are an expert travel planner. Generate a detailed, day-by-day travel itinerary in JSON format.

Output ONLY valid JSON matching this schema:
{
  "tripTitle": "string",
  "startDate": "YYYY-MM-DD",
  "endDate": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "location": "City/Area name",
      "isTravel": false,
      "activities": "Detailed day plan with times",
      "food": "Specific dish and restaurant recommendations",
      "places": "Specific places/addresses",
      "transport": "Local transport notes"
    }
  ],
  "transports": [
    {"from": "Origin", "to": "Dest", "mode": "Mode", "duration": "Time", "notes": "Tips"}
  ],
  "tips": ["Tip 1", "Tip 2"],
  "packingList": ["Item 1", "Item 2"],
  "budgetEstimate": {
    "accommodation": "$", "transport": "$", "food": "$",
    "activities": "$", "total": "$", "currency": "USD"
  }
}

Rules:
- Output ONLY the JSON object, no markdown
- Use the user's exact dates and leg order
- For travel days: focus on transit logistics
- Budget in USD for mid-range traveler"""

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response

@app.route("/api/generate", methods=["POST", "OPTIONS"])
def generate():
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "OpenRouter API key not configured"}), 500

    trip = request.get_json()
    if not trip or not trip.get("legs"):
        return jsonify({"error": "At least one leg required"}), 400

    legs_text = "\n".join([
        f"  {leg['date']}: {leg['location']}{' (TRAVEL DAY)' if leg.get('isTravel') else ''}"
        f"\n    Activities: {leg.get('activities', '—')}"
        f"\n    Food: {leg.get('food', '—')}"
        f"\n    Places: {leg.get('places', '—')}"
        for leg in trip["legs"]
    ])

    user_prompt = f"""Trip: {trip.get('tripTitle', 'My Trip')}
Dates: {trip.get('startDate', '?')} to {trip.get('endDate', '?')}
Route: {trip.get('routeSummary', '—')}

Legs (in order, keep these dates/locations exactly):
{legs_text}

Generate the full itinerary JSON now."""

    try:
        payload = json.dumps({
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 8000,
        }).encode()

        req = urllib.request.Request(
            f"{OPENROUTER_BASE}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://trip-planner.vercel.app",
                "X-Title": "Trip Planner",
            }
        )

        with urllib.request.urlopen(req, timeout=90) as resp:
            body = json.loads(resp.read())

        content = body["choices"][0]["message"]["content"].strip()
        content = re.sub(r'^```(?:json)?\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'\s*```$', '', content, flags=re.MULTILINE)

        result = json.loads(content)
        return jsonify(result)

    except json.JSONDecodeError as e:
        return jsonify({"error": f"Model returned invalid JSON: {e}"}), 502
    except urllib.error.HTTPError as e:
        return jsonify({"error": f"OpenRouter HTTP error: {e.code} {e.read().decode()}"}), 502
    except Exception as e:
        return jsonify({"error": f"Generation failed: {str(e)}"}), 500

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": MODEL})