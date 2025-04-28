import os
from openai import AsyncOpenAI

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

async def summarize_text(text: str) -> str:
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"Summarize the following text:\n\n{text}\n\nSummary:"
    
    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    
    print(response)
    
    return response.choices[0].message.content.strip()


