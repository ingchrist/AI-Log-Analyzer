def extract_response_text(response) -> str:
    if hasattr(response, 'content'):
        content = response.content
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            return '\n'.join([b['text'] if isinstance(b, dict) else str(b) for b in content]).strip()
    return str(response).strip()
