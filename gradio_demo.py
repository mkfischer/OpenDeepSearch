from smolagents import CodeAgent, LiteLLMModel
from opendeepsearch import OpenDeepSearchTool
import os
from dotenv import load_dotenv
import argparse
import gradio as gr

# Load environment variables
load_dotenv()

# Add command line argument parsing
parser = argparse.ArgumentParser(description='Run the Gradio demo with custom models')
parser.add_argument('--model-name', 
                   default="openrouter/google/gemini-2.0-flash-001",
                   help='Model name for search')
parser.add_argument('--orchestrator-model', 
                   default="openrouter/google/gemini-2.0-flash-001",
                   help='Model name for orchestration')
parser.add_argument('--reranker',
                   choices=['jina', 'infinity'],
                   default='jina',
                   help='Reranker to use (jina or infinity)')
parser.add_argument('--share',
                   action='store_true',
                   help='Create a public share link')

args = parser.parse_args()

# Use the command line arguments
search_tool = OpenDeepSearchTool(model_name=args.model_name, reranker=args.reranker)
model = LiteLLMModel(
    model_id=args.orchestrator_model,
    temperature=0.2,
)

# Initialize the agent with the search tool
agent = CodeAgent(tools=[search_tool], model=model)

# Create a custom Gradio interface
with gr.Blocks(title="OpenDeepSearch Demo") as demo:
    gr.Markdown("# OpenDeepSearch Demo")
    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(
                label="Your question",
                placeholder="Ask me anything...",
                lines=2
            )
            submit_btn = gr.Button("Submit")
        
        with gr.Column():
            output = gr.Markdown(label="Response")
    
    def process_query(query):
        response = agent.run(query)
        return response
    
    submit_btn.click(
        fn=process_query,
        inputs=user_input,
        outputs=output
    )

# Launch the custom UI with server name set for container
demo.launch(server_name="0.0.0.0", share=args.share)
