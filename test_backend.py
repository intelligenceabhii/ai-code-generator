
import sys
import os
from langchain_core.messages import HumanMessage

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

try:
    from coder import coder_agent
    
    print("Agent loaded successfully.")
    print("Invoking agent...")
    
    events = coder_agent.stream(
        {
            "messages": [HumanMessage(content="Write a function to add two numbers")],
            "attempts": 0,
            "error_flag": "unknown",
        },
        stream_mode="values",
    )
    
    for event in events:
        print(event)
        
    print("Agent execution complete.")

except Exception as e:
    print(f"Error: {e}")
