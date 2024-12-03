from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
openai_key= os.getenv("OPENAI_KEY")
client = OpenAI(api_key=openai_key)


def get_openai_response():
    prompt = (
    f"hello "

)
    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "system", "content": prompt}],
    max_tokens=2000,
    temperature=0.7,
    )
    travel_plan = response.choices[0].message.content
    print("success")
    print(travel_plan)
    return travel_plan

print(get_openai_response())