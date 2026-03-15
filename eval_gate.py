import os
import sys
import json
import pandas as pd
from rag_system import rag_app, vector_store, seed_data
from ragas import evaluate
from ragas.metrics import faithfulness
from langchain_ollama import ChatOllama
import pandas as pd

# Load Golden Dataset
def load_dataset(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def run_evaluation():
    print("---RUNNING EVALUATION GATE---")
    seed_data()
    
    dataset = load_dataset("golden_dataset.json")
    results = []
    
    for item in dataset:
        print(f"Testing query: {item['question']}")
        response = rag_app.invoke({"question": item["question"]})
        results.append({
            "question": item["question"],
            "answer": response["answer"],
            "contexts": response["context"],
            "ground_truth": item["ground_truth"]
        })
    
    # Convert to Ragas dataset
    from datasets import Dataset
    ragas_dataset = Dataset.from_pandas(pd.DataFrame(results))
    
    # Configure Ragas with local Ollama model
    eval_llm = ChatOllama(model="llama3.2", temperature=0)
    
    # Run Ragas Evaluation
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from langchain_ollama import OllamaEmbeddings
    
    llm_wrapper = LangchainLLMWrapper(eval_llm)
    emb_wrapper = LangchainEmbeddingsWrapper(OllamaEmbeddings(model="llama3.2"))
    
    # In newer Ragas, we use the EvaluationDataset and evaluate function differently
    from ragas import EvaluationDataset
    
    eval_results = evaluate(
        dataset=ragas_dataset,
        metrics=[faithfulness],
        llm=llm_wrapper,
        embeddings=emb_wrapper
    )
    
    faithfulness_scores = eval_results["faithfulness"]
    if isinstance(faithfulness_scores, list):
        avg_faithfulness = sum(filter(None, faithfulness_scores)) / len([x for x in faithfulness_scores if x is not None])
    else:
        avg_faithfulness = faithfulness_scores
        
    print(f"\nAverage Faithfulness: {avg_faithfulness}")
    
    if avg_faithfulness < 0.85:
        print(f"FAIL: Faithfulness score {avg_faithfulness} is below threshold of 0.85")
        sys.exit(1)
    else:
        print(f"PASS: Faithfulness score {avg_faithfulness} is above threshold")
        sys.exit(0)

if __name__ == "__main__":
    try:
        run_evaluation()
    except Exception as e:
        print(f"ERROR DURING EVALUATION: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
