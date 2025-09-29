import json
from tts_utils import load_catalog, filter_tts, find_records

# Load once
catalog = load_catalog("tts_catalog.json")

# 1) Which providers can do Hindi in India?
print(filter_tts(catalog, language="Spanish", country="", provider=""))
# -> ['OpenAI', 'AWS Polly', 'Azure AI Speech', 'Basten', 'Cartesia', 'ElevenLabs', 'Gemini', 'LMNT', 'Neuphonic', 'PlayHT', 'ResembleAI', 'SarvamAI', 'SmallestAI']

# # 2) Which providers cover Spanish for Mexico?
# print(filter_tts(catalog, language="Spanish", country="Mexico"))

# # 3) Everything a specific provider supports in a country (e.g., Azure in UAE)
# print(find_records(catalog, country="United Arab Emirates", provider="Azure AI Speech"))

# # 4) Quick “available anywhere” by language (no country constraint)
# print(filter_tts(catalog, language="Swedish"))

# # 5) Full rows for debugging
# rows = find_records(catalog, language="French", country="Senegal")
# for r in rows:
#     print(r["provider"], r["countries"])
