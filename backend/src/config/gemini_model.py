"""
Model configuration adapted from gemini_model.py reference file.

This module provides model configuration using OpenRouter/Gemini with fallbacks.
"""
import os
from agents import (
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig
)
from ..config import settings


# Try OpenRouter first (as configured in settings)
openrouter_key = settings.OPENROUTER_KEY
base_url = settings.BASE_URL or "https://openrouter.ai/api/v1"
model_name = settings.MODEL or "gemini/gemini-2.5-flash"

# Check if we can initialize the model - first try OpenRouter
client = None
geminiModel = None
MODEL_AVAILABLE = False
config = None

if openrouter_key:
    try:
        # Try to use OpenRouter API
        client = AsyncOpenAI(
            api_key=openrouter_key,
            base_url=base_url,
        )

        geminiModel = OpenAIChatCompletionsModel(
            openai_client=client,
            model=model_name,
        )

        # Test the client with a simple operation to check if quota is exceeded
        MODEL_AVAILABLE = True
    except Exception as e:
        print(f"OpenRouter API unavailable (possibly quota exceeded): {e}")
        # OpenRouter failed, try direct Gemini access
        client = None
        geminiModel = None

# If OpenRouter is not available or failed, try direct Gemini access
if not MODEL_AVAILABLE:
    gemini_api_key = settings.GEMINI_API_KEY
    if gemini_api_key:
        try:
            gemini_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
            client = AsyncOpenAI(
                api_key=gemini_api_key,
                base_url=gemini_base_url,
            )

            geminiModel = OpenAIChatCompletionsModel(
                openai_client=client,
                model="gemini-2.5-flash",  # Using gemini-2.5-flash model
            )

            MODEL_AVAILABLE = True
        except Exception as e:
            print(f"Gemini API also unavailable: {e}")
            client = None
            geminiModel = None
            MODEL_AVAILABLE = False

# If neither OpenRouter nor Gemini worked, try OpenAI as fallback
if not MODEL_AVAILABLE:
    openai_api_key = settings.OPENAI_API_KEY
    if openai_api_key:
        try:
            openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            client = AsyncOpenAI(
                api_key=openai_api_key,
                base_url=openai_base_url,
            )

            geminiModel = OpenAIChatCompletionsModel(
                openai_client=client,
                model="gpt-3.5-turbo",  # Using gpt-3.5-turbo as a fallback
            )

            MODEL_AVAILABLE = True
        except Exception as e:
            print(f"OpenAI API also unavailable: {e}")
            client = None
            geminiModel = None
            MODEL_AVAILABLE = False

# configuring the model/config - only if models are available
if MODEL_AVAILABLE and geminiModel is not None:
    config = RunConfig(
        model=geminiModel,
        model_provider=client,
        tracing_disabled=True
    )
else:
    config = None
    geminiModel = None
    client = None
    MODEL_AVAILABLE = False