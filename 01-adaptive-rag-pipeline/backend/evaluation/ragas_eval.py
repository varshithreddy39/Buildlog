import json
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

from datasets import Dataset

from ragas import evaluate

from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
load_dotenv()
evaluation_llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API"),
    model="llama-3.1-8b-instant"
)


embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
with open(
    "evaluation/results.json",
    "r"
) as f:

    results = json.load(f)


dataset = Dataset.from_dict({

    "question": [
        item["question"]
        for item in results
    ],

    "answer": [
        item["answer"]
        for item in results
    ],

    "contexts": [
        item["contexts"]
        for item in results
    ],

    "ground_truth": [
        item["ground_truth"]
        for item in results
    ]

})


score = evaluate(

    dataset=dataset,

    metrics=[

        faithfulness,

        answer_relevancy,

        context_precision,

        context_recall
    ],llm=evaluation_llm,embeddings=embedding_model
)

print("\n========== RAGAS RESULTS ==========\n")

print(score)