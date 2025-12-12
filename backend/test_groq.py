"""
Test script to verify Groq integration
"""
from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Test simple JSON response
prompt = """Return a JSON object with these fields:
- name: "test"
- score: 85
- items: ["a", "b", "c"]

Return ONLY the JSON, no markdown or extra text."""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Return ONLY valid JSON with no markdown."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.3
)

content = response.choices[0].message.content.strip()
print("Raw response:")
print(content)
print("\n" + "="*50 + "\n")

# Extract JSON if wrapped in markdown
if content.startswith("```"):
    content = content.split("```json")[-1] if "```json" in content else content.split("```")[-1]
    content = content.split("```")[0].strip()
    print("Extracted JSON:")
    print(content)
    print("\n" + "="*50 + "\n")

try:
    data = json.loads(content)
    print("Parsed successfully!")
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Parse error: {e}")
