import validators
from .fetcher import fetch_url_content
from .parser import parse_html
from .summarizer import summarize_text

async def process_url(url: str) -> str:
    """Process a URL and return its summary"""
    try:
        raw_url = url
        print(f"├── Processing URL: {raw_url}")
        url = raw_url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"
        print(f"├── Normalized URL: {url}")
        
        if validators.url(url) == True:
            print("├── 🔍 Fetching URL content...")
            html = await fetch_url_content(url)
            print("├── 📝 Parsing HTML...")
            text = parse_html(html)
            print(f"├── 📊 Extracted text length: {len(text)} characters")
            print("├── 🤖 Requesting OpenAI summary...")
            summary = await summarize_text(text[:5000])
            print(f"├── ✅ Summary generated: {len(summary)} characters")
            print(f"└── Summary preview: {summary[:100]}...")
            return summary
        else:
            print(f"└── ❌ Invalid URL format")
            return "Invalid URL"
    except Exception as e:
        print(f"└── ❌ Error in URL processing: {str(e)}")
        raise e 