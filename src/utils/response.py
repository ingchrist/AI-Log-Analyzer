def extract_response_text(response) -> str:
    if hasattr(response, 'content'):
        content = response.content
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts = []
            for b in content:
                if isinstance(b, dict):
                    parts.append(b.get('text', str(b)))
                else:
                    parts.append(str(b))
            return '\n'.join(parts).strip()
    return str(response).strip()
