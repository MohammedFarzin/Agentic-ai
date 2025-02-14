from openai import OpenAI
import os
import re
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def llm_call(prompt: str, system_prompt: str, model="gpt-4o-mini") -> str:
    # Calls the model and return the response
    client = OpenAI()
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        system_message={"content": system_prompt},
        max_tokens=4096,
        temperature=0.2
    )
    return response.choices[0].message.content


def extract_xml(text: str, tag: str) -> str:
    # Extracs the content of the specified XLM tag from the given text. Used for parsing structured responses

    match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
    return match.group(1) if match else ""