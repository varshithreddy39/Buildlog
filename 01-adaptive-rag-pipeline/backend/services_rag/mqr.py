from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API")
)
def generate_multi_query(query):
    prompt=f"""
You are an expert retrieval query expansion system.

Generate 3 alternative search queries
that would help retrieve relevant information
from academic transcripts and student records.

The generated queries should:
- preserve original meaning
- include possible academic terminology
- include likely keywords present in documents
- improve retrieval quality

Return ONLY the queries.
One query per line.

User Query:
{query}
"""
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "system",
                "content": "You generate alternative queries for better document retrieval."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3
    )

    generated_text = response.choices[0].message.content.strip()
    expanded_queries=[ q.strip() for q in generated_text.split("\n") if q.strip()]

    expanded_queries.insert(0, query)

    expanded_queries = list(
        dict.fromkeys(expanded_queries)
    )
    return expanded_queries

