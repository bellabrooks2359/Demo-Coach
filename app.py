from flask import Flask, request, jsonify, render_template
import os
import openai
import json
from supabase import create_client

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

SYSTEM_PROMPT = """
You are the Sisuu Reflection Coach - warm, empowering, and clear. Not too soppy / fluffy - this is for professionals and graduates - it can be clear and supportive but sound human. You guide users to reflect on how they work best and generate a structured Cognitive profile that will be shared with recruiters & HR so they can have a more holistic picture of who they are and what they bring.

You ask thoughtful, honest questions. You affirm the user while helping them articulate their real needs. The important thing here is to really encourage them to think both over the course of their life & their career. There is no right or wrong answer, you are trying to get to the essence of who they are.

You're a wise coach and a good friend - not afraid to name things with care and clarity.

After each of the sections of reflection, summarise their response into short, clear insights using soft, affirming language. This should be broken down into a high level summary & key bullet points.

At the end, generate a structured Sisuu Profile using the format below:

[final profile structure unchanged for brevity]
"""

questions = [
    "What were you drawn to as a child?",
    "What activities made time disappear for you?",
    "What did others praise you for growing up or in past roles?",
    "What feels easy for you but hard for others?",
    "When do you feel most in flow?",
    "What do people often ask you for help with?",
    "What do you do differently that works well?",
    "If all roles/expectations fell away, what would still be true about you?",
    "When have you felt quietly powerful?",
    "How would a close friend describe what’s uniquely great about you?",
]

user_histories = {}

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    user_id = request.json.get("user_id")

    if not user_input or not user_id:
        return jsonify({"error": "Missing user_id or message"}), 400

    if user_id not in user_histories:
        user_histories[user_id] = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT}
            ],
            "step": 0,
            "insights": [],
            "awaiting_confirmation": True
        }
        return jsonify({"response": "Welcome back! Would you like to continue from where you left off, or start fresh?"})

    history = user_histories[user_id]

    if history.get("awaiting_confirmation", False):
        if user_input.lower() in ["yes", "y", "continue", "resume"]:
            history["awaiting_confirmation"] = False
            first_question = questions[history["step"]]
            response = f"Great — let's pick up where we left off. \n\n➡️ {first_question}"
            history["messages"].append({"role": "assistant", "content": response})
            return jsonify({"response": response})

        elif user_input.lower() in ["no", "n", "start", "restart"]:
            user_histories[user_id] = {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "assistant", "content": "Hi again! 👋 Let's start fresh.\n\n➡️ What were you drawn to as a child?"}
                ],
                "step": 0,
                "insights": [],
                "awaiting_confirmation": False
            }
            return jsonify({"response": "Hi again! 👋 Let's start fresh.\n\n➡️ What were you drawn to as a child?"})

        else:
            return jsonify({"response": "Would you like to continue from where you left off, or start fresh?"})

    history["messages"].append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=history["messages"]
        )
        reply = response.choices[0].message["content"]
        history["messages"].append({"role": "assistant", "content": reply})
        history["step"] += 1

        if history["step"] >= len(questions):
            final_summary_prompt = "Please now create the final profile using everything above. Output it in structured JSON using the Sisuu format."
            history["messages"].append({"role": "user", "content": final_summary_prompt})

            final_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=history["messages"]
            )
            full_profile = final_response.choices[0].message["content"]

            try:
                structured_output = json.loads(full_profile)
                save_sisuu_profile(structured_output.get("MySisuu Profile", {}))
                save_productivity_profile(structured_output.get("Productivity Profile", {}))
                del user_histories[user_id]
                return jsonify({"response": full_profile, "structured": structured_output})
            except json.JSONDecodeError:
                return jsonify({"response": full_profile, "warning": "Unstructured output"})

        next_question = questions[history["step"]]
        formatted_reply = f"{reply}\n\n---\n\n➡️ {next_question}"
        return jsonify({"response": formatted_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["GET"])
def chat_ui():
    return render_template("chat.html")

@app.route("/mysisuu/<name>")
def view_profile(name):
    result = supabase.table("sisuu_profiles").select("*").eq("name", name).single().execute()
    profile = result.data
    if not profile:
        return "Profile not found", 404
    return render_template("mysisuu.html", profile=profile)

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
            "Thrives on autonomy, challenge, and ambiguity",
            "Creative, non-conventional, and fast learner"
        ],
        "Strengths": [
            "Pattern recognition in people",
            "Fast autonomous learner",
            "Creative strategist",
            "Connector and practical problem-solver",
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
            "Focuses on building culture and trust as a foundation for process",
            "Empowers team members to lead and own outcomes"
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
You are Sisuu – a coaching assistant that helps candidates reflect on how to navigate situations with their manager using both cognitive and leadership profiles.

Here's the candidate profile:
{json.dumps(candidate_profile, indent=2)}

Here's their manager's profile:
{json.dumps(manager_profile, indent=2)}

Your response must:
1. Briefly name the potential dynamic or friction
2. Offer thoughtful, affirming coaching based on both styles
3. Suggest a next step or approach the candidate can try
4. Use warm, clear, and professional language – never generic

Candidate's Question:
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

def save_sisuu_profile(profile_data):
    supabase.table("sisuu_profiles").insert(profile_data).execute()

def save_productivity_profile(productivity_data):
    supabase.table("productivity_profiles").insert(productivity_data).execute()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
