import ollama

def research_content(topic, audience):

    prompt = f"""
    You are a content research agent.

    Topic: {topic}
    Target Audience: {audience}

    Give:
    1. Trending content ideas
    2. Audience interests
    3. Content angles
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