# filepath: /pdf-reader-backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure_search import search_azure, index_pdf_content
import os
import uuid

app = Flask(__name__)
CORS(app)

# Define forbidden topics
FORBIDDEN_TOPICS = ["politics", "religion", "violence", "hate speech"]


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

def contains_forbidden_topics(text):
    for topic in FORBIDDEN_TOPICS:
        if topic.lower() in text.lower():
            return True
    return False

@app.route('/api/upload', methods=['POST'])
def upload():
    
    pdf_file = request.files['pdf']
    pdf_text = extract_text_from_pdf(pdf_file)
    
    # Generate a unique ID for the document
    doc_id = str(uuid.uuid4())
    
    # Index the PDF content
    index_pdf_content(doc_id, pdf_text)

    return jsonify({'message': 'PDF content indexed successfully', 'doc_id': doc_id})


@app.route('/api/ask', methods=['POST'])
def ask():
    
    data = request.get_json()
    doc_id = data.get('doc_id')
    question = data.get('question')
    if not doc_id or not question:
        return jsonify({'error': 'Document ID and question are required'}), 400
    
    # Use Azure Search to get answers and facts
    relevant_content  = search_azure(question,doc_id)

    # Combine the relevant content into a single prompt
    combined_content = "\n".join(relevant_content)
    prompt = f"Based on the following content:\n{combined_content}\n\nAnswer the question: {question}"
    
    answer = ask_gpt(prompt)

    # Check for forbidden topics
    if contains_forbidden_topics(answer):
        answer = "I'm sorry, but I cannot discuss this topic."
        
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)