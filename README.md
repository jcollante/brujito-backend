# brujito-backend
backend-proyecto que se conecta con chatgpt for chatbot para dar una respuesta

# Deploying the Chatbot API on Google Cloud Functions

## Prerequisites

1. **Google Cloud CLI**:
   - Ensure you have the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and authenticated.
   - Authenticate using:
     ```bash
     gcloud auth login
     ```

2. **Google Cloud Project**:
   - Set the active project for deployment:
     ```bash
     gcloud config set project brujitos-chatbot
     ```
   - Replace `brujitos-chatbot` with your Google Cloud project ID.

3. **Enable Required APIs**:
   - Enable Cloud Functions:
     ```bash
     gcloud services enable cloudfunctions.googleapis.com
     ```
   - Enable Secret Manager:
     ```bash
     gcloud services enable secretmanager.googleapis.com --project=brujitos-chatbot
     ```

4. **Prepare Secrets in Secret Manager**:
   - Create a secret for the OpenAI API key:
     ```bash
     echo -n "YOUR_OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=-
     ```
   - Replace `YOUR_OPENAI_API_KEY` with your actual OpenAI API key.
   - Grant access to the Cloud Function’s service account:
     ```bash
     gcloud secrets add-iam-policy-binding openai-api-key --member="serviceAccount:brujitos-chatbot@appspot.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
     ```

---

## File Structure

Ensure your code files are organized as follows:


---

## Deployment Command

```bash
gcloud services enable cloudbuild.googleapis.com --project=brujitos-chatbot
```

Run the following `gcloud` command to deploy the function:

```bash
gcloud functions deploy chatgpt-api-backend \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --entry-point main \
    --region europe-west3 \
    --no-gen2 \
    --set-env-vars GCP_PROJECT_ID=brujitos-chatbot,OPENAI_SECRET_NAME=openai-api-key
```

Replace:
chatgpt-api-backend: The name of your function.
python310: The runtime version for Python (adjust if needed).
YOUR_REGION: The region where you want to deploy the function (e.g., us-central1).
brujitos-chatbot: Your Google Cloud project ID.


Post-Deployment
Get the Function URL:

After deployment, the command will output the URL of your function. It will look something like:
arduino
https://REGION-PROJECT_ID.cloudfunctions.net/chatgpt-api-backend
Test the API:

Use tools like curl, Postman, or your frontend to send requests to the function URL. For example:
bash
Code kopieren
curl -X POST https://europe-west3-brujitos-chatbot.cloudfunctions.net/chatgpt-api-backend/chat \
    -H "Content-Type: application/json" \
    -H "Origin: https://reqbin.com/curl" \
    -d '{"message": "How can I manage stress?"}'
Monitor Logs:

View logs to troubleshoot or monitor the function:
bash
Code kopieren
gcloud functions logs read chatgpt-api-backend
