import streamlit as st
import requests
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SUPER_MEME_API_KEY = os.getenv("SUPER_MEME_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Streamlit app setup
st.title("AI Meme Generator")
st.markdown("Transform your ideas into hilarious memes with AI!")

# Input field for meme idea
meme_text = st.text_area("Describe your meme idea...", max_chars=300)
char_count = len(meme_text)

st.write(f"Character count: {char_count}/300")

# Function to generate meme
def generate_meme(prompt):
    try:
        headers = {
            'Authorization': f'Bearer {SUPER_MEME_API_KEY}',
            'Content-Type': 'application/json'
        }

        logging.info(f"Sending meme generation request to Super Meme API for prompt: '{prompt[:50]}...'")
        response = requests.post(
            'https://app.supermeme.ai/api/v2/meme/image',
            json={'text': prompt},
            headers=headers
        )

        if response.status_code == 401:
            logging.error("Super Meme API returned 401 Unauthorized. Check API key.")
            return None

        response.raise_for_status()

        memes = response.json().get('memes', [])
        logging.info(f"Successfully generated {len(memes)} memes from Super Meme API.")
        return memes[:10]  # Return top 10 memes

    except requests.exceptions.RequestException as e:
        logging.error(f"API request to Super Meme failed: {e}")
        return None
    except Exception as e:
        logging.exception("Unexpected error during meme generation:")
        return None

# Button to generate meme
if st.button("Generate Meme"):
    if meme_text.strip():
        memes = generate_meme(meme_text.strip())
        if memes:
            for url in memes:
                st.image(url)
        else:
            st.error("Failed to generate memes. Try again.")
    else:
        st.error("Please enter a meme idea.")

# Function to get meme ideas
def get_meme_idea():
    try:
        prompt = ("give me 10 meme ideas that are relatable to pneumonia vaccine, "
                  "pneumonia is not flu, misinformation about pneumonia, and "
                  "other things related to pneumonia. i want those in a positive "
                  "tone. the ideas should be in casual bahasa indonesia.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        logging.info("Sending request to Gemini API for meme ideas.")
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code != 200:
            logging.error(f"Failed to get meme ideas from Gemini API. Status Code: {response.status_code}")
            return None

        candidates = response_data.get('candidates')
        if not candidates or not isinstance(candidates, list):
            logging.error("Invalid Gemini API response structure: No candidates or not a list.")
            return None

        content = candidates[0].get('content')
        if not content or not isinstance(content, dict):
            logging.error("Invalid Gemini API response structure: No content or not a dictionary.")
            return None

        parts = content.get('parts')
        if not parts or not isinstance(parts, list):
            logging.error("Invalid Gemini API response structure: No parts or not a list.")
            return None

        text_response = parts[0].get('text', '').strip()
        if not text_response:
            logging.warning("Empty response received from Gemini API (no text in parts).")
            return None

        ideas_list = [idea.strip() for idea in text_response.split("\n") if idea.strip()]
        logging.info(f"Successfully retrieved {len(ideas_list)} meme ideas from Gemini API.")
        return ideas_list

    except requests.exceptions.RequestException as e:
        logging.error(f"API request to Gemini failed: {e}")
        return None
    except Exception as e:
        logging.exception("Unexpected error during idea generation:")
        return None

# Button to get meme ideas
if st.button("Get Meme Ideas"):
    ideas = get_meme_idea()
    if ideas:
        st.subheader("Meme Ideas:")
        for idea in ideas:
            st.write(f"- {idea}")
    else:
        st.error("Failed to get meme ideas. Try again.")
