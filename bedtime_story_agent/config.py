import os

# --- Environment Variables ---
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
ARTIFACT_SERVICE_URI = os.getenv("ARTIFACT_SERVICE_URI")

# --- Model Names ---
MODEL_TEXT_GENERATION = "gemini-2.5-flash"
MODEL_IMAGE_GENERATION = "gemini-2.5-flash"
MODEL_AUDIO_GENERATION = "gemini-2.5-flash"

# --- Agent Configuration ---
ART_STYLE_PROMPT = "in a gentle, friendly cartoon style suitable for a children's bedtime story"
NARRATOR_VOICE = "en-US-Wavenet-J" # Example voice