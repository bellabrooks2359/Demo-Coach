from flask import Flask, request, jsonify, render_template, redirect
import os
import openai
import json
from supabase import create_client

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@app.route("/coach", methods=["POST"])
def coach():
    data = request.json
    question = data.get("question", "")

    candidate_profile = {
        "Name": "Mohsin",
        "Summary": "Pattern-spotter and structured problem-solver who reimagines systems to unlock human potential.",
        "Cognitive Style": [
            "Generalist with cross-domain thinking",
            "Balances detail orientation with big-picture strategy",
            "Thrives on autonomy, challenge, and ambiguity"
        ],
        "Strengths": [
            "Pattern recognition in people",
            "Fast autonomous learner",
            "Creative strategist",
            "Resilient and non-conventional"
        ],
        "Motivators": [
            "Freedom through impact",
            "Long-term legacy",
            "Integrity without ego"
        ]
    }

    manager_profile = {
        "Name": "Sarah Johnson",
        "Summary": "Engineering leader who blends technical strategy with human-centred team development.",
        "Leadership Style": [
            "Balances technical depth with strategic thinking",
            "Prioritises psychological safety and team development",
            "Focuses on building culture and trust as a foundation for process"
        ],
        "Strengths": [
            "Technical leadership with human focus",
            "Strategic communication across levels",
            "Systems thinking for team dynamics"
        ],
        "Values": [
            "Psychological safety first",
            "Sustainable excellence (avoids burnout culture)"
        ]
    }

    system_prompt = f"""
You are Sisuu — a smart, calm coaching assistant.

Your goal is to help candidates navigate specific work situations with their manager, using their cognitive and leadership profiles for context.

**Tone**: conversational, warm but clear. Never fluffy, never corporate. You sound like someone emotionally intelligent and grounded — not like a therapist or an HR person.

Here’s the candidate’s cognitive profile:
{json.dumps(candidate_profile, indent=2)}

Here’s the manager’s leadership profile:
{json.dumps(manager_profile, indent=2)}

**Response structure**:

1. Start conversationally. Ask a short, open follow-up question that invites the user to share one more detail, if helpful.

2. Then offer 2–3 bitesize suggestions grounded in the profiles above. These should:
   - Name the tension or contrast clearly
   - Offer a suggested phrase or action
   - Be brief and specific — no long paragraphs, no general advice

3. If it’s unclear what the candidate’s asking, say so and ask them to rephrase.

Examples of your phrasing:
- “Try something like: ‘I’m keen to run with this, but a clearer start point would help me move faster.’”
- “Sounds like autonomy is high, but clarity’s low. Can you ask what success looks like?”
- “Might be worth saying: ‘What would good look like here, just so I’m aligned before I go off and build?’”

Only generate what’s useful. Be human. Cut the fluff.

Candidate’s message:
\"\"\"{question}\"\"\"
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message["content"]
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/coach-demo")
def coach_demo():
    return render_template("coach_demo.html")

@app.route("/")  # Root route
def index():
    return redirect("/coach-demo")

@app.after_request
def allow_iframe(response):
    response.headers["X-Frame-Options"] = "ALLOWALL"
    return response
