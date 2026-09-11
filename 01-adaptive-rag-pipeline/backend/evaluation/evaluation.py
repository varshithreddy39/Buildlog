import os
import sys

sys.path.append("/app")
import json 

from services_rag.pipline import question_answer_pipeline,handle_upload

with open("transcript.pdf","rb") as f:

    file_content = f.read()

    filename = "transcript.pdf"

    handle_upload(file_content, filename)

with open("Adp resume.pdf","rb") as f:

    file_content = f.read()

    filename = "Adp resume.pdf"

    handle_upload(file_content, filename)

with open("benchmark_dataset.json", "r") as f:

    benchmark_data = json.load(f)

    results = []

for item in benchmark_data:

    question = item["question"]

    ground_truth = item["ground_truth"]

    print(f"\nQuestion: {question}")
    print(f"Ground Truth: {ground_truth}")

    response = question_answer_pipeline(question)

    result = {
        "question": question,

        "ground_truth": ground_truth,

        "answer": response["answer"],

        "contexts": response["contexts"]    
    }
    results.append(result)

with open(
    "evaluation/results.json",
    "w"
) as f:

        json.dump(
            results,
            f,
            indent=4
        )

print("\nEvaluation dataset generated successfully.")