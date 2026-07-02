import ollama

def review_content(content):

    prompt = f"""
    You are a content review agent.

    Check this content:

    {content}

    Improve:
    1. Grammar
    2. Engagement
    3. Clarity
    4. Make it more attractive for audience
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