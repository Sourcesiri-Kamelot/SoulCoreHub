# ✅ LIVE - Loads Hugging Face token securely
import os

def get_huggingface_token():
    return os.getenv("HUGGINGFACE_API_TOKEN")  # Set this in your .env or shell
