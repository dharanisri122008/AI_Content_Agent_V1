import ollama

def create_content(research):

    prompt = f"""
    You are a content creation agent.

    Use this research:

    {research}

    Create:
    1. Social media caption
    2. Short description
    3. Hashtags
    4. Call to action
    """

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]