import os
import time
from typing import List, Dict, Any, TypedDict
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from observability import setup_observability, estimate_cost, count_tokens, flush_traces

# Initialize Observability
ENABLE_PHOENIX = os.getenv("ENABLE_PHOENIX", "true").lower() == "true"
session = setup_observability() if ENABLE_PHOENIX else None

# Initialize Embeddings and LLM
embeddings = OllamaEmbeddings(model="llama3.2")
llm = ChatOllama(model="llama3.2", temperature=0)

# Vector Store Setup
PERSIST_DIR = "./chroma_db"
vector_store = Chroma(
    collection_name="rag_collection",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR
)

# Seed sample data if empty
def seed_data():
    if len(vector_store.get()["ids"]) == 0:
        print("---SEEDING DATA---")
        texts = [
            "LangGraph is a library for building stateful, multi-actor applications with LLMs.",
            "ChromaDB is an open-source embedding database for AI applications.",
            "Arize Phoenix is a tool for observability and evaluation of LLM applications.",
            "RAGAS is a framework for evaluating Retrieval Augmented Generation systems.",
            "Llama 3.2 is a state-of-the-art open source large language model from Meta."
        ]
        vector_store.add_texts(texts)

# State Definition
class GraphState(TypedDict):
    question: str
    context: List[str]
    answer: str
    ttft: float
    cost: float
    precision_score: float

# Nodes
def retrieve(state: GraphState):
    print("---RETRIEVING---")
    question = state["question"]
    docs = vector_store.similarity_search(question, k=3)
    context = [doc.page_content for doc in docs]
    return {"context": context}

def generate(state: GraphState):
    print("---GENERATING---")
    question = state["question"]
    context = state["context"]
    
    prompt = ChatPromptTemplate.from_template("""
    You are a helpful assistant. Use the following context to answer the question.
    Context: {context}
    Question: {question}
    Answer:
    """)
    
    chain = prompt | llm
    
    start_time = time.time()
    ttft = 0
    full_response = ""
    
    # Measure TTFT (Time To First Token)
    for chunk in llm.stream(prompt.format(context=context, question=question)):
        if ttft == 0:
            ttft = time.time() - start_time
        full_response += chunk.content
        
    return {"answer": full_response, "ttft": ttft}

def collector(state: GraphState):
    print("---COLLECTING METRICS---")
    question = state["question"]
    context = state["context"]
    answer = state["answer"]
    
    # Calculate Cost
    input_text = f"{question} {' '.join(context)}"
    input_tokens = count_tokens(input_text)
    output_tokens = count_tokens(answer)
    cost = estimate_cost(input_tokens, output_tokens)
    
    # Simple Precision Score (Demonstration)
    keywords = set(" ".join(context).lower().split())
    answer_words = set(answer.lower().split())
    if keywords:
        precision = len(keywords.intersection(answer_words)) / len(keywords)
    else:
        precision = 0.0
        
    print(f"TTFT: {state['ttft']:.4f}s")
    print(f"Estimated Cost: ${cost:.6f}")
    print(f"Precision Score (Simulated): {precision:.4f}")
    
    return {"cost": cost, "precision_score": precision}

# Build Graph
builder = StateGraph(GraphState)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_node("collector", collector)

builder.set_entry_point("retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", "collector")
builder.add_edge("collector", END)

rag_app = builder.compile()

if __name__ == "__main__":
    seed_data()
    example_input = {"question": "What is LangGraph?"}
    result = rag_app.invoke(example_input)
    print("\n---FINAL RESULT---")
    print(f"Answer: {result['answer']}")
    print(f"Metrics: TTFT={result['ttft']:.4f}s, Cost=${result['cost']:.6f}")
    
    # Keep session alive for a bit to view dashboard
    flush_traces()
    if session:
        print(f"\n🚀 Phoenix Dashboard available at: {session.url}")
        print("Traces are being sent... Keep this script running to view the dashboard.")
        print("Waiting for 120 seconds for you to inspect... (Press Ctrl+C to stop)")
        try:
            time.sleep(120)
        except KeyboardInterrupt:
            print("\nStopped.")
    else:
        print("\nPhoenix Dashboard could not be launched locally.")
        print("However, instrumentation is active. If a dashboard is already running at http://localhost:6006, please check it now.")
        print("Waiting for 30 seconds for traces to flush...")
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            print("\nStopped.")
