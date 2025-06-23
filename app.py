from flask import Flask, render_template, request, jsonify
import openai
import subprocess
import webbrowser
import os
from dotenv import load_dotenv
from assistant import run_Kiwi_ai


load_dotenv()
openai.api_key = "YOUR API KEY HERE"

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    if not request.is_json:
        return jsonify({"reply": "Invalid request format."}), 400

    data = request.get_json()
    user_input = data.get("message", "")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        reply = response.choices[0].message["content"]
    except Exception as e:
        print("OpenAI Error:", e)
        reply = "I'm having trouble connecting to OpenAI."

    return jsonify({"reply": reply})

@app.route("/voice", methods=["POST"])
def handle_voice_request():
    if not request.is_json:
        return jsonify({"response": "Invalid request format"}), 400

    user_input = request.json.get("text", "")
    if not user_input:
        return jsonify({"response": "Empty input received"}), 400

    print("Voice input:", user_input)

    try:
        reply = run_Kiwi_ai(user_input)
    except Exception as e:
        print("Kiwi AI Error:", e)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_input}]
            )
            reply = response.choices[0].message["content"]
        except Exception as e:
            print("OpenAI Fallback Error:", e)
            reply = "I'm having trouble connecting to OpenAI."

    return jsonify({"response": reply})

@app.route("/action", methods=["POST"])
def action():
    try:
        command = request.json.get("command", "").lower()
        print(f"Checking action for: {command}")

        if "open youtube" in command:
            webbrowser.open("https://youtube.com")
        elif "open google" in command:
            webbrowser.open("https://google.com")
        elif "open weather" in command:
            webbrowser.open("https://weather.com")
        elif "open notes" in command:
            subprocess.run(["open", "-a", "Notes"])
        elif "open safari" in command:
            subprocess.run(["open", "-a", "Safari"])
        elif "open vs code" in command or "open code" in command:
            subprocess.run(["open", "-a", "Visual Studio Code"])
        elif "shutdown" in command or "exit" in command:
            os._exit(0)

        return jsonify({"status": "ok"})

    except Exception as e:
        print("Action error:", e)
        return jsonify({"status": "failed", "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
