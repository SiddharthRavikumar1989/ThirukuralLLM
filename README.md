# Thirukural Scholar RAG App

A conversational AI assistant that provides wisdom from the Thirukural. Built with Streamlit, LangChain, and OpenAI.

## 🚀 Deployment to Streamlit Community Cloud

This app is ready for deployment! Follow these steps:

### 1. Push to GitHub
1. Create a new repository on GitHub.
2. Initialize git in this folder (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```
   *(Note: The `.gitignore` file ensures your API keys in `.env` and the local database `chroma_db` are NOT pushed for security)*

### 2. Connect to Streamlit Cloud
1. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and sign in.
2. Click **"New app"**.
3. Select your GitHub repository.
4. Set the **Main file path** to `app.py`.

### 3. Configure Secrets (CRITICAL)
Your app needs the OpenAI API Key to work. Since `.env` is ignored, you must add it securely in Streamlit Cloud:

1. In the app deployment screen (or App Settings > Secrets), find "Advanced settings".
2. Add your secret in TOML format:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
3. Click "Save".

### 4. Deploy!
- Click **"Deploy"**.
- On the first run, the app will automatically build the Thirukural vector database (this might take 1-2 minutes).
- Once built, the "Scholar" will be ready to answer!

## Local Development
To run locally:
```bash
pip install -r requirements.txt
streamlit run app.py
```
