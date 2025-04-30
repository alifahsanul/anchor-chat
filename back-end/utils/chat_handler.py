from openai import AsyncOpenAI
import os
from .fetcher import fetch_url_content
from .parser import parse_html

async def process_chat_request(question: str, url: str, chat_history: list) -> str:
    """Process a chat request and return AI response"""
    try:
        # Format chat history for context
        chat_context = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in chat_history[-5:]
        ])
        print("├── 📜 Previous Messages:")
        for msg in chat_history[-5:]:
            print(f"│   {msg['role']}: {msg['content'][:50]}...")
        
        # Get URL content if provided
        url_context = ""
        if url:
            print("├── 🔍 Fetching URL content...")
            html = await fetch_url_content(url)
            text = parse_html(html)
            url_context = f"\nURL Content Summary: {text[:2000]}..."
            print(f"├── 📊 URL context length: {len(url_context)} characters")
        
        # Prepare prompt for OpenAI
        prompt = f"""Context from URL: {url_context}

Previous conversation:
{chat_context}

User Question: {question}

Please provide a helpful response based on the context and question."""

        print("├── 🤖 Sending request to OpenAI...")
        
        # Get response from OpenAI
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        
        ai_response = response.choices[0].message.content.strip()
        print(f"├── ✅ Response received: {len(ai_response)} characters")
        print(f"└── Response preview: {ai_response[:100]}...")
        
        return ai_response
        
    except Exception as e:
        print(f"└── ❌ Error in chat processing: {str(e)}")
        raise e 