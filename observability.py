import os
import time
import phoenix as px
from openinference.instrumentation.langchain import LangChainInstrumentor
import tiktoken

# Global tracer provider for flushing
_TRACER_PROVIDER = None

def setup_observability():
    global _TRACER_PROVIDER
    print("---SETTING UP OBSERVABILITY---")
    
    # Check for active session
    session = px.active_session()
    if session:
        print(f"Connected to active Phoenix session at: {session.url}")
    else:
        print("Note: No local Phoenix session found in this process. Traces will be sent to http://localhost:6006.")

    # ALWAYS Setup Instrumentation
    try:
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from openinference.instrumentation.langchain import LangChainInstrumentor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        endpoint = "http://localhost:6006/v1/traces"
        exporter = OTLPSpanExporter(endpoint=endpoint)
        _TRACER_PROVIDER = TracerProvider()
        
        span_processor = BatchSpanProcessor(exporter)
        _TRACER_PROVIDER.add_span_processor(span_processor)
        
        try:
            LangChainInstrumentor().uninstrument()
        except:
            pass
            
        LangChainInstrumentor().instrument(tracer_provider=_TRACER_PROVIDER)
        print(f"Instrumentation active. Exporting to: {endpoint}")
    except Exception as e:
        print(f"FAILED TO SETUP INSTRUMENTATION: {e}")

    return session

def flush_traces():
    global _TRACER_PROVIDER
    if _TRACER_PROVIDER:
        print("Flushing traces...")
        _TRACER_PROVIDER.force_flush()

# Cost Calculation Constants (Simulated GPT-4o Pricing)
# Input: $2.50 / 1M tokens
# Output: $10.00 / 1M tokens
INPUT_COST_PER_TOKEN = 2.50 / 1_000_000
OUTPUT_COST_PER_TOKEN = 10.00 / 1_000_000

def estimate_cost(input_tokens, output_tokens):
    return (input_tokens * INPUT_COST_PER_TOKEN) + (output_tokens * OUTPUT_COST_PER_TOKEN)

def count_tokens(text: str, model="gpt-4o"):
    # Using tiktoken as a proxy for token counting
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))
