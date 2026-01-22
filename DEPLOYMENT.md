# Streamlit Community Cloud Deployment Guide

## Prerequisites

1. GitHub account
2. Streamlit Community Cloud account (https://streamlit.io/cloud)
3. Gemini API key (for AI features)

## Step 1: Push to GitHub

```bash
# Navigate to project directory
cd C:\Users\Bala Sankar\Downloads\acc_new_sum\AI-Repo

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Streamlit Cloud deployment"

# Add remote (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/summarization-accelerator.git

# Push to GitHub
git push -u origin main
```

## Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click **"New app"**
3. Select your GitHub repository
4. Set the following:
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click **"Deploy!"**

## Step 3: Configure Secrets

After deployment, add your API keys:

1. Go to your app's **Settings** → **Secrets**
2. Add the following:

```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
```

3. Click **"Save"**

## Step 4: Update App to Use Secrets (Optional)

To auto-load the API key from secrets instead of manual input, modify `app.py`:

```python
# In the sidebar configuration section
api_key = st.text_input(
    "Gemini API Key",
    value=st.secrets.get("GEMINI_API_KEY", ""),
    type="password"
)
```

## Important Notes

### Resource Limits

- **Memory**: 1GB (Community Cloud free tier)
- **Large models** (T5, PEGASUS) may hit memory limits
- Consider disabling abstractive models for cloud deployment

### File Storage

- Streamlit Cloud is **ephemeral** - files are cleared on reboot
- Generated reports won't persist between sessions
- Consider adding cloud storage (GCS, S3) for production

### Model Loading

- First run will be slow (downloading models)
- Subsequent runs will be faster (cached)

## Troubleshooting

### "Module not found" errors

- Check `requirements.txt` includes all dependencies

### Memory errors

- Disable large abstractive models
- Use smaller model variants (e.g., `t5-small` instead of `t5-base`)

### NLTK data errors

- The app auto-downloads NLTK data on startup
- If issues persist, check `nltk.txt` file exists

## Files Created for Deployment

```
AI-Repo/
├── app.py                    # Main Streamlit app
├── requirements.txt          # Python dependencies
├── nltk.txt                  # NLTK data packages
├── .streamlit/
│   ├── config.toml           # Theme configuration
│   └── secrets.toml          # API keys (local only, not committed)
├── .gitignore                # Excludes secrets & generated files
└── src/                      # Core modules
```

## Live URL

After deployment, your app will be available at:

```
https://YOUR_APP_NAME.streamlit.app
```

Share this URL with your team!
