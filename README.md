# 🛡️ SentinelRAG: Production-Grade Observability Pipeline

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20(Llama%203.2)-orange.svg)](https://ollama.com/)
[![Arize Phoenix](https://img.shields.io/badge/Observability-Arize%20Phoenix-green.svg)](https://phoenix.arize.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

SentinelRAG is a high-performance RAG (Retrieval-Augmented Generation) system built with **LangGraph** and **ChromaDB**, focused on extreme observability. It provides real-time metrics, node-level tracing, and automated CI/CD gating—all running **100% locally and for free** using Ollama.

## 🚀 Key Features

-   **Deep Instrumentation**: Every graph node (Retrieve, Generate, Collector) is traced using OpenInference and exported to a local Arize Phoenix dashboard.
-   **Real-time Metrics**:
    -   **TTFT (Time to First Token)**: Measure the responsiveness of your local LLM.
    -   **Simulated Cost**: Track token usage mapped to industry-standard pricing (GPT-4o).
    -   **Context Precision**: Automatic evaluation of retrieval quality.
-   **CI/CD Gating**: Standalone evaluation script that validates the system against a golden dataset using RAGAS Faithfulness scores.
-   **Persistent Dashboard**: Dedicated background launcher ensures your observability data is always accessible.

## 🛠️ Tech Stack

-   **Orchestration**: LangGraph
-   **Vector Database**: ChromaDB
-   **Embedding & LLM**: Ollama (Llama 3.2)
-   **Observability**: Arize Phoenix / OpenTelemetry
-   **Evaluation**: RAGAS
-   **Tokenizer**: Tiktoken

## 📥 Installation

1.  **Clone the Repository**:
    ```bash
    git clone e:/SentinelRAG
    cd SentinelRAG
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Ollama**:
    Ensure [Ollama](https://ollama.com/) is running and the model is pulled:
    ```bash
    ollama pull llama3.2
    ```

## 🚦 Usage

### 1. Launch the Observability Dashboard
Run the dedicated launcher in a separate terminal:
```bash
python launch_phoenix.py
```
Access the dashboard at: [http://localhost:6006](http://localhost:6006)

### 2. Run the RAG System
Execute the main RAG pipeline:
```bash
python rag_system.py
```

### 3. Run CI/CD Evaluation Gate
Test the system against the `golden_dataset.json`:
```bash
python eval_gate.py
```
*Note: The script exits with status 1 if the Faithfulness score is < 0.85.*

## 📊 Metrics Explained

-   **TTFT**: The delay between the request and the first generated token. Critical for UX.
-   **Cost**: Simulated dollars based on $2.50 per 1M input tokens and $10.00 per 1M output tokens.
-   **Faithfulness (RAGAS)**: Measures how well the answer is derived solely from the retrieved context.

## 🔒 Privacy & Cost
Everything runs locally. No data leaves your machine, and no API keys are required for the core functionality.

---
Built with ❤️ for High-Performance RAG Engineering.
