# filepath: /pdf-reader-backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)



# Load environment variables from .env.local file
load_dotenv(dotenv_path='.env.local')

client = AzureOpenAI(
    api_key=os.getenv("API_KEY"),
    api_version=os.getenv("API_VERSION"),
    azure_endpoint=os.getenv("AZURE_ENDPOINT")
)

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

def ask_gpt(prompt):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/api/ask', methods=['POST'])
def ask():
    pdf_file = request.files['pdf']
    question = request.form['question']
    #question = "how are u?"
    pdf_text = extract_text_from_pdf(pdf_file)
    prompt = f"{pdf_text}\n\nQuestion: {question}"
    answer = ask_gpt(prompt)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)