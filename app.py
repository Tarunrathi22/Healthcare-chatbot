from flask import Flask, request, jsonify, render_template
from markupsafe import Markup
import requests
import re

app = Flask(__name__)

API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Improved HTML response formatter
def organize_response(text):
    # Bold markdown (**text**) → <b>text</b>
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.*?)\*\*", r"<b>\1</b>", text)  # Handle *text**

    # Process line-by-line
    lines = text.strip().split("\n")
    html_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            html_lines.append("<br>")
        elif stripped.startswith("•") or stripped.startswith("*") or stripped.startswith("-"):
            html_lines.append(f"<li>{stripped[1:].strip()}</li>")
        elif re.match(r"^\d+\.", stripped):  # numbered list
            html_lines.append(f"<li>{stripped}</li>")
        elif stripped.startswith("🔹"):
            html_lines.append(f"<p>{stripped}</p>")
        else:
            html_lines.append(f"<p>{stripped}</p>")

    # Wrap <li> items in <ul>
    final_output = []
    in_list = False
    for line in html_lines:
        if line.startswith("<li>"):
            if not in_list:
                final_output.append("<ul>")
                in_list = True
            final_output.append(line)
        else:
            if in_list:
                final_output.append("</ul>")
                in_list = False
            final_output.append(line)
    if in_list:
        final_output.append("</ul>")

    return Markup("".join(final_output))

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "healthcare-chatbot"
    }

    body = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "user", "content": user_message}]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=body)
        data = response.json()

        raw_text = data['choices'][0]['message']['content']
        formatted = organize_response(raw_text)

        return jsonify({"response": formatted})

    except Exception as e:
        print("Error:", e)
        return jsonify({"response": f"❌ Error occurred: {str(e)}"})

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
