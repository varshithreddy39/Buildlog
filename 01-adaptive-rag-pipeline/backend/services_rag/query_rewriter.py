from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API")
)


def rewrite_query(
    query,
    history,
    summary=""
):

    conversation_history = ""

    for chat in history:

        conversation_history += (
            f"User: {chat['user']}\n"
            f"Assistant: {chat['assistant']}\n\n"
        )
    prompt = f"""
You are a Query Rewriting Assistant.

Your task is to rewrite the user's current query into a clear standalone query using the conversation summary and recent conversation.

Rules:

1. Preserve the user's original intent exactly.
2. Do NOT answer the question.
3. Do NOT change the meaning of the question.
4. Do NOT replace a broad question with a narrower one.
5. Resolve references such as:
   - he
   - she
   - his
   - her
   - it
   - they
   - them
   - this
   - that
   - these
   - those
   - first
   - second
   - highest
   - lowest
6. If the query is already clear, return it unchanged.
7. Return ONLY the rewritten query.

Examples:

User Query: What about his education?
Output: What are Venkata Varshith Reddy Mettukuru's education details?

User Query: What about his skills?
Output: What are Venkata Varshith Reddy Mettukuru's skills?

User Query: his role
Output: What roles has Venkata Varshith Reddy Mettukuru held?

User Query: second highest
Output: Which subject has the second highest grade?

================ CONVERSATION SUMMARY ================

{summary}

================ RECENT CONVERSATION ================

{conversation_history}

================ CURRENT QUERY ================

{query}

================ STANDALONE QUERY ================
"""

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "system",
                "content": (
                    "You rewrite conversational queries "
                    "into standalone questions."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.1
    )

    rewritten_query = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    return rewritten_query