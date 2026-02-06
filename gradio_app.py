import sys
import os
import gradio as gr
from langchain_core.messages import HumanMessage
import json

# Add backend to path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from coder import coder_agent

def generate_code_stream(prompt, history):
    """
    Generator function for Gradio to stream updates.
    """
    try:
        # Initialize state for stream
        history = history or []
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": ""})
        
        # Initial status
        current_status = "INITIALIZING"
        current_code = ""
        current_logs = ""
        
        yield (
            history, 
            f"Status: {current_status}",
            current_code,
            current_logs
        )

        # Stream agent execution
        events = coder_agent.stream(
            {
                "messages": [HumanMessage(content=prompt)],
                "attempts": 0,
                "error_flag": "unknown",
            },
            stream_mode="values",
        )
        
        for event in events:
            # Extract current state
            error_flag = event.get("error_flag", "unknown")
            attempts = event.get("attempts", 0)
            code_solution = event.get("code_solution")
            messages = event.get("messages", [])

            # Update logs with latest message if available
            if messages:
                last_msg = messages[-1]
                msg_content = getattr(last_msg, "content", str(last_msg))
                # Append to logs (simulated console)
                current_logs += f"\n> {str(msg_content)[:200]}..." 

            # Determine status
            if error_flag == "unknown":
                status = "GENERATING"
            elif error_flag == "yes":
                status = f"RETRYING (Attempt {attempts}/3)"
            elif error_flag == "no":
                status = "CHECKING"
            else:
                status = "PROCESSING"

            # Update code if solution exists
            if code_solution:
                # Format code block
                current_code = f"# {code_solution.prefix}\n\n{code_solution.imports}\n\n{code_solution.code}"
            
            # Update assistant's last message
            history[-1]["content"] = "Thinking..." 
            
            yield (
                history,
                f"Status: {status}",
                current_code,
                current_logs
            )

        # Final update
        history[-1]["content"] = "Code generation complete! Check the panel on the right."
        yield (
            history,
            "Status: COMPLETE",
            current_code,
            current_logs
        )

    except Exception as e:
        history[-1]["content"] = f"Error: {str(e)}"
        yield (
            history,
            f"Status: ERROR: {str(e)}",
            current_code,
            current_logs + f"\nERROR: {str(e)}"
        )

# Create Gradio UI
with gr.Blocks(title="AI Code Generator") as demo:
    gr.Markdown("# 🤖 AI Code Generator")
    gr.Markdown("Self-correcting code generation")
    
    with gr.Row():
        with gr.Column(scale=1):
            chatbot = gr.Chatbot(label="Conversation", height=400)
            
            with gr.Row():
                msg = gr.Textbox(label="Enter your prompt", placeholder="Enter your prompt here", scale=4)
                submit_btn = gr.Button("Submit", variant="primary", scale=1)
                stop_btn = gr.Button("Stop", variant="stop", scale=1)
            
            clear = gr.Button("Clear History")
            
            with gr.Accordion("Agent Logs", open=False):
                logs_box = gr.TextArea(label="Logs", interactive=False, max_lines=10)

        with gr.Column(scale=1):
            # Moved Status to the top of the right column
            status_box = gr.Textbox(label="Status", interactive=False)
            code_output = gr.Code(label="Generated Code", language="python", interactive=False)

    # Wire up the events
    
    # Enter key triggers generation
    submit_event_msg = msg.submit(
        generate_code_stream, 
        inputs=[msg, chatbot], 
        outputs=[chatbot, status_box, code_output, logs_box]
    )
    
    # Submit button triggers generation
    submit_event_btn = submit_btn.click(
        generate_code_stream,
        inputs=[msg, chatbot],
        outputs=[chatbot, status_box, code_output, logs_box]
    )
    
    # Stop button cancels both events
    stop_btn.click(fn=None, cancels=[submit_event_msg, submit_event_btn])
    
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
