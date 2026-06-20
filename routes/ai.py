from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from connect_ai.agent.agent import ConnectAgent

# Create Blueprint
ai = Blueprint("ai", __name__)

# Create Agent Instance
agent = ConnectAgent()


# --------------------------------------------------
# Main AI endpoint
# --------------------------------------------------
@ai.route("/ai", methods=["POST"])
@login_required
def run_ai():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "Message is empty"}), 400


    result = agent.run(user_input)

    return jsonify(result)


# --------------------------------------------------
# AI Reply Suggestion for Messages
# --------------------------------------------------
@ai.route("/ai/suggest-reply", methods=["POST"])
@login_required
def suggest_reply():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    suggestion = agent.suggest_reply(user_id)

    return jsonify({"suggestion": suggestion})


# --------------------------------------------------
# Test AI Page
# --------------------------------------------------
@ai.route("/ai-page")
@login_required
def ai_page():
    return render_template("ai.html")