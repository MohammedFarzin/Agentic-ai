from openai import OpenAI
import os
import re
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def llm_call(prompt: str,model="gpt-4o") -> str:
    # Calls the model and return the response
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=4096,
        temperature=0.2
    )
    return response.choices[0].message.content


def extract_xml(text: str, tag: str) -> str:
    # Extracs the content of the specified XLM tag from the given text. Used for parsing structured responses

    match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
    return match.group(1) if match else ""