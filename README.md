---
title: Crop Disease Detection
emoji: 🌿
colorFrom: green
colorTo: gray
sdk: docker
app_port: 7860
---

# Edge AI Crop Disease Detection

This project is a Django crop disease detection app with a chatbot assistant.
It is configured to run as a Hugging Face Docker Space.

## Required Secrets

Add these in your Space settings:

- `GROQ_API_KEY`
- `GROQ_MODEL` if you want to override the default model
- `SECRET_KEY` if you want to replace the local fallback
- `MODEL_WEIGHTS_PATH` if your deployed weights live in a different location

## Notes

- The app runs on port `7860` in Hugging Face Spaces.
- Static files are served through WhiteNoise.
- Django is started with Gunicorn.
- If you upload the full project repository, make sure the trained model weights
  are included or adjust `MODEL_WEIGHTS_PATH` to point to the deployed file.

## Local Development

```bash
pip install -r requirements.txt
python manage.py runserver
```
