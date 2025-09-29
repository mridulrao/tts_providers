import os
from openai import OpenAI, AzureOpenAI
import json
from tqdm import tqdm
from lancedb import connect
import pyarrow as pa
from dotenv import load_dotenv

load_dotenv()


def get_language_country_mapping(language_set):   
    system_prompt = """
    You are a multilingual geography assistant that maps world languages to the countries where they are spoken. 
    When the user provides a list of languages, respond **only** with a valid JSON object.

    ### Rules:
    1. The **key** must be the exact language name as provided by the user (preserve casing).
    2. The **value** must be a JSON array (list) of country names where the language is spoken.
    3. Include both **official** and **major regional usage** countries.
    4. The output must contain **no extra text, comments, or explanations** — only raw JSON.
    5. If a language name is unrecognized, still include it with an empty list [].

    Example Input:
    Afrikaans, Arabic, Hindi

    Example Output:
    {
      "Afrikaans": ["South Africa", "Namibia"],
      "Arabic": ["Egypt", "Saudi Arabia", "Iraq", "Syria", "Jordan", "Lebanon", "Morocco", "Algeria", "Tunisia", "Sudan", "Yemen", "United Arab Emirates", "Qatar", "Bahrain", "Oman", "Libya", "Kuwait", "Palestine"],
      "Hindi": ["India", "Fiji", "Nepal"]
    }
    """

    try:
        openai_client = OpenAI()

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": language_set}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        # The model's response is a JSON string, which needs to be parsed
        extracted_data = response.choices[0].message.content
        extracted_data = json.loads(extracted_data)
        return extracted_data

    except Exception as e:
        print(f"An error occurred during document processing: {e}")
        return {}


languages_string = '''

English, French, German, Spanish, Portuguese.
'''


output = get_language_country_mapping(languages_string)
print(output)







