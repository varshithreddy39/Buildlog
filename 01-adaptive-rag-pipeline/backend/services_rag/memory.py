from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API")
)


def summarize_prompt(
    old_summary="",
    chat_history=None
):

    conversation_history = ""

    if chat_history:

        for chat in chat_history:

            conversation_history += (
                f"User: {chat['user']}\n"
                f"Assistant: {chat['assistant']}\n\n"
            )

    prompt = f"""
You are a conversation summarization assistant.

Update the existing conversation summary using the new conversation.

Keep:
- important facts
- user preferences
- important questions and answers
- important decisions
- important entities and topics discussed

Remove:
- repetitive information
- unnecessary details

Make the summary concise but informative.

================ EXISTING SUMMARY ================

{old_summary}

================ NEW CONVERSATION ================

{conversation_history}

================ UPDATED SUMMARY ================
"""

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "system",
                "content": "You summarize conversations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2
    )

    return response.choices[0].message.content