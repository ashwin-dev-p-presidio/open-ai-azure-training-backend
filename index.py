from openai import AzureOpenAI
from pdf_extractor import extract_text_from_pdf
from dotenv import load_dotenv
import os

# Load environment variables from .env.development file
load_dotenv(dotenv_path='.env.development')

client = AzureOpenAI(
    api_key = os.getenv("API_KEY"),
    api_version = os.getenv("API_VERSION"),
    azure_endpoint = os.getenv("AZURE_ENDPOINT")
)

# Define a function to interact with gpt
def ask_gpt(prompt):
    try:
        # Call the OpenAI API to generate a response
      completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt
            }
          ]
        )

      return completion.choices[0].message.content

    except Exception as e:
        print(f"Error: {e}")
        return None

# Example prompt
user_prompt = "What is the capital of India?"

# Get GPT's response
gpt_response = ask_gpt(user_prompt)

# Print the response
print("GPT:", gpt_response)