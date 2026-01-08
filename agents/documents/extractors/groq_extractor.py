import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_fields_with_groq(raw_text: str, doc_type: str) -> dict:
    """
    Use Groq to extract structured fields from OCR text
    """

    prompt = f"""
You are a document intelligence system.

Document type: {doc_type}

Extract the following fields if present:
- document_number
- organization_name
- issue_date
- expiry_date

Return STRICT JSON only.

OCR Text:
{raw_text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except Exception:
        return {
            "error": "Failed to parse document",
            "raw_response": content
        }
