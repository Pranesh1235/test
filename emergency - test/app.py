from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
import logging # Import logging

app = Flask(__name__)
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # Configure logging

SUPER_MEME_API_KEY = os.getenv("SUPER_MEME_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_meme():
    try:
        data = request.get_json()
        prompt = data.get('text', '').strip()

        if not prompt or len(prompt) > 300:
            logging.warning(f"Invalid prompt length received: '{prompt}'") # Log warning
            return jsonify({'error': 'Invalid prompt length. Must be between 1 and 300 characters.'}), 400

        headers = {
            'Authorization': f'Bearer {SUPER_MEME_API_KEY}',
            'Content-Type': 'application/json'
        }

        logging.info(f"Sending meme generation request to Super Meme API for prompt: '{prompt[:50]}...'") # Log API request
        response = requests.post(
            'https://app.supermeme.ai/api/v2/meme/image',
            json={'text': prompt},
            headers=headers
        )

        if response.status_code == 401:
            logging.error("Super Meme API returned 401 Unauthorized. Check API key.") # Log error
            return jsonify({'error': 'Unauthorized. Check your API key.'}), 401

        response.raise_for_status()

        memes = response.json().get('memes', [])
        logging.info(f"Successfully generated {len(memes)} memes from Super Meme API.") # Log success
        return jsonify({'memes': memes[:10]})

    except requests.exceptions.RequestException as e:
        logging.error(f"API request to Super Meme failed: {e}") # Log detailed error
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except Exception as e:
        logging.exception("Unexpected error during meme generation:") # Log full exception with traceback
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/get_idea', methods=['GET'])
def get_idea():
    try:
        prompt = ("give me 10 meme ideas that relatable to pneumonia vaccine, "
                  "pneumonia is not flu, misinformation about pneumonia, and "
                  "other things related to pneumonia. i want those in positive "
                  "tone. the ideas should be in casual bahasa indonesia. you just "
                  "need to give the ideas, dont suggest any caption, images, "
                  "emojis, etc. be sharp and crisp and punchy don't verbose also don't give the number like 1,2 for 10 sentence also * too")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        logging.info("Sending request to Gemini API for meme ideas.") # Log API request
        response = requests.post(url, json=payload, headers=headers)
        logging.debug(f"Gemini API Response Status Code: {response.status_code}") # Log debug info
        logging.debug(f"Gemini API Response Text: {response.text}") # Log debug info

        response_data = response.json()

        if response.status_code != 200:
            logging.error(f"Failed to get meme ideas from Gemini API. Status Code: {response.status_code}, Response: {response_data}") # Log error with details
            return jsonify({'error': f'Failed to get meme ideas from Gemini API: {response_data}'}), 500

        candidates = response_data.get('candidates')
        if not candidates or not isinstance(candidates, list):
            logging.error("Invalid Gemini API response structure: No candidates or not a list.") # Log structure error
            return jsonify({'error': 'Invalid response structure: No candidates or not a list'}), 500

        if not candidates:
            logging.warning("Gemini API returned no candidates.") # Log warning
            return jsonify({'error': 'Gemini API returned no candidates'}), 500

        content = candidates[0].get('content')
        if not content or not isinstance(content, dict):
            logging.error("Invalid Gemini API response structure: No content or not a dictionary.") # Log structure error
            return jsonify({'error': 'Invalid response structure: No content or not a dictionary'}), 500

        parts = content.get('parts')
        if not parts or not isinstance(parts, list):
            logging.error("Invalid Gemini API response structure: No parts or not a list.") # Log structure error
            return jsonify({'error': 'Invalid response structure: No parts or not a list'}), 500

        if not parts:
            logging.warning("Gemini API returned empty parts.") # Log warning
            return jsonify({'error': "Gemini API returned empty parts"}), 500

        text_response = parts[0].get('text', '').strip()

        if not text_response:
            logging.warning("Empty response received from Gemini API (no text in parts).") # Log warning
            return jsonify({'error': 'Empty response received from API (no text in parts)'}), 500

        ideas_list = [idea.strip() for idea in text_response.split("\n") if idea.strip()]
        logging.info(f"Successfully retrieved {len(ideas_list)} meme ideas from Gemini API.") # Log success
        return jsonify({'ideas': ideas_list})

    except requests.exceptions.RequestException as e:
        logging.error(f"API request to Gemini failed: {e}") # Log detailed error
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except Exception as e:
        logging.exception("Unexpected error during idea generation:") # Log full exception with traceback
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)