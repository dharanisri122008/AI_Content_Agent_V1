import ollama

def create_schedule(content):

    prompt = f"""
    You are a social media scheduling agent.

    Content:
    {content}

    Create a weekly posting schedule.

    Include:
    - Day
    - Best time
    - Post idea
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