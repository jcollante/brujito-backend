import os
import openai
from flask import Flask, request, jsonify
from google.cloud import secretmanager
from functools import wraps

# Flask app setup
app = Flask(__name__)

# Allowed frontend origin
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "https://your-frontend-url.com")

# Define prohibited topics or keywords
PROHIBITED_TOPICS = [
    "violence",
    "hate speech",
    "illegal activities",
    "explicit content",
    "self-harm",
    "political campaigning",
    "sensitive personal information"
]

# Define the context and expected answers
CONTEXT = "You are an AI assistant specialized in helping users with health and wellness advice, focusing on fitness, nutrition, and mental health tips. Avoid medical diagnoses or legal advice."
EXPECTED_TOPICS = [
    "fitness routines",
    "healthy eating habits",
    "mental health tips",
    "stress management",
    "wellness strategies"
]

# Fetch OpenAI API key from Google Cloud Secret Manager
def get_secret(secret_name, project_id):
    client = secretmanager.SecretManagerServiceClient()
    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=secret_path)
    return response.payload.data.decode("UTF-8")

# Set project ID and secret name
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-google-cloud-project-id")
OPENAI_SECRET_NAME = os.getenv("OPENAI_SECRET_NAME", "openai-api-key")

# Retrieve OpenAI API key from Secret Manager
try:
    OPENAI_API_KEY = get_secret(OPENAI_SECRET_NAME, PROJECT_ID)
    openai.api_key = OPENAI_API_KEY
except Exception as e:
    OPENAI_API_KEY = None
    print(f"Error accessing OpenAI API key: {e}")

# Helper decorator to check CORS and enforce allowed origin
def cors_and_origin_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        origin = request.headers.get("Origin")
        if origin != ALLOWED_ORIGIN:
            return jsonify({"error": "Forbidden origin"}), 403
        
        response = f(*args, **kwargs)
        if isinstance(response, tuple):
            response[0].headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            return response
        elif isinstance(response, Flask.response_class):
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        return response
    return decorated_function

# Function to check for prohibited topics
def contains_prohibited_topics(message):
    lower_message = message.lower()
    for topic in PROHIBITED_TOPICS:
        if topic.lower() in lower_message:
            return True
    return False

# Function to ensure the user query aligns with expected topics
def aligns_with_expected_topics(message):
    lower_message = message.lower()
    for topic in EXPECTED_TOPICS:
        if topic.lower() in lower_message:
            return True
    return False

# ChatGPT API endpoint
@app.route('/chat', methods=['POST'])
@cors_and_origin_check
def chat():
    # Verify OpenAI API key is set
    if not OPENAI_API_KEY:
        return jsonify({"error": "OpenAI API key not configured"}), 500

    # Extract message from request
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid request, 'message' field is required"}), 400

    message = data['message']

    # Check for prohibited topics
    if contains_prohibited_topics(message):
        return jsonify({
            "error": "Your message contains prohibited topics. Please follow the usage guidelines."
        }), 400

    # Check if the query aligns with expected topics
    if not aligns_with_expected_topics(message):
        return jsonify({
            "error": "Your message does not align with the chatbot's expected topics. Please ask about fitness, nutrition, mental health, or wellness strategies."
        }), 400

    # Make OpenAI ChatGPT API call with context
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Specify the desired model
            messages=[
                {"role": "system", "content": CONTEXT},
                {"role": "user", "content": message}
            ],
        )
        chat_response = response['choices'][0]['message']['content']
        return jsonify({"response": chat_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
@cors_and_origin_check
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # Flask app runs only locally, use Google Cloud Functions for deployment
    app.run(host='0.0.0.0', port=8080)
