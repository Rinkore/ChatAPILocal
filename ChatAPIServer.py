from flask import Flask, request
import openai
from flask_cors import CORS
import toml

app = Flask(__name__)
CORS(app, resources=r'/*')
with open("config.toml") as f:
    data = toml.load(f)
openai.api_key = data["ChatGPT"]["ApiKey"]


@app.route("/translate", methods=["POST"])
def translate():
    prompt = request.form.get("prompt")
    message = request.form.get("message")
    top_p = float(request.form.get("top_p"))
    temperature = float(request.form.get("temperature"))
    response = openai.ChatCompletion.create(
        messages=[
            {"role": "system", "content": prompt},
            {'role': 'user', 'content': message}
        ],
        top_p=top_p,
        n=1,
        stop=None,
        temperature=temperature,
        model="gpt-3.5-turbo",
        stream=False
    )
    translation = response
    return translation


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
