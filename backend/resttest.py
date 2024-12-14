import os
import json

from dotenv import load_dotenv

load_dotenv()

firestore_key = os.getenv("FIRESTORE_KEY")
if not firestore_key:
    raise ValueError("FIRESTORE_KEY environment variable is missing or improperly loaded.")

try:
    service_account_info = json.loads(firestore_key)
except json.JSONDecodeError as e:
    print(f"Error decoding FIRESTORE_KEY: {e}")
    print("Raw FIRESTORE_KEY content:", firestore_key)
    raise