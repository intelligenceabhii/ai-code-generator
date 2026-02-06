# ============================================================
# Imports
# ============================================================

from typing import TypedDict, Annotated, List

from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.graph import StateGraph, END


# ============================================================
# LLM Configuration
# ============================================================

def get_llm():
    return ChatOpenAI(
        model="openai/gpt-oss-20b",   # must match vLLM model name
        temperature=0,
        api_key="EMPTY",              # ignored by vLLM
        base_url="http://localhost:5005/v1",
    )


llm = get_llm()


# ============================================================
# Prompt Template
# ============================================================

CODE_GEN_SYS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a coding assistant.
Ensure any code you provide can be executed with all required imports and variables defined.
Structure your answer as follows:
1) a prefix describing the solution
2) the imports (if no imports needed keep it empty)
3) executable code blocks"""
        ),
        ("user", "{question}")
    ]
)


# ============================================================
# Structured Output Schema
# ============================================================

class Code(BaseModel):
    """Schema for code solutions."""
    prefix: str = Field(description="Description of the problem and approach")
    imports: str = Field(description="Only import statements")
    code: str = Field(description="Executable code without imports")


code_generator = llm.with_structured_output(Code)


# ============================================================
# LangGraph State Definition
# ============================================================

class CodeGenState(TypedDict):
    """
    Represents the state of the coding graph.
    """
    error_flag: str
    messages: Annotated[List[AnyMessage], add_messages]
    code_solution: Code
    attempts: int


# ============================================================
# Graph Nodes
# ============================================================

def generate_code(state: CodeGenState) -> CodeGenState:
    print("--- GENERATING CODE SOLUTION ---")

    messages = state["messages"]
    attempts = state["attempts"]

    # ✅ Pass messages directly
    code_solution = code_generator.invoke(messages)

    messages.append(
        HumanMessage(
            content=(
                f"Here is my solution attempt:\n\n"
                f"Description:\n{code_solution.prefix}\n\n"
                f"Imports:\n{code_solution.imports}\n\n"
                f"Code:\n{code_solution.code}"
            )
        )
    )

    return {
        "messages": messages,
        "code_solution": code_solution,
        "attempts": attempts + 1,
        "error_flag": "unknown",
    }



def check_code_execution(state: CodeGenState) -> CodeGenState:
    """Validate imports and execution of generated code."""
    print("--- CHECKING CODE EXECUTION ---")

    messages = state["messages"]
    code_solution = state["code_solution"]
    attempts = state["attempts"]

    # ---------------- Import Check ----------------
    try:
        exec(code_solution.imports)
    except Exception as e:
        print("--- CODE IMPORT CHECK: FAILED ---")
        messages.append((
            "user",
            f"""Import test failed!

Exception:
{e}

Please fix the import section."""
        ))
        return {
            "messages": messages,
            "code_solution": code_solution,
            "attempts": attempts,
            "error_flag": "yes",
        }

    # ---------------- Execution Check ----------------
    try:
        scope = {}
        exec(f"{code_solution.imports}\n{code_solution.code}", scope)
    except Exception as e:
        print("--- CODE EXECUTION CHECK: FAILED ---")
        messages.append((
            "user",
            f"""Your code failed during execution!

Exception:
{e}

1) Explain what went wrong
2) Fix the solution
Return the FULL solution (prefix, imports, code)."""
        ))
        return {
            "messages": messages,
            "code_solution": code_solution,
            "attempts": attempts,
            "error_flag": "yes",
        }

    print("--- NO ERRORS FOUND ---")
    return {
        "messages": messages,
        "code_solution": code_solution,
        "attempts": attempts,
        "error_flag": "no",
    }


# ============================================================
# Routing Logic
# ============================================================

MAX_ATTEMPTS = 3


def decide_next(state: CodeGenState) -> str:
    """Decide whether to retry or finish."""
    if state["error_flag"] == "no" or state["attempts"] >= MAX_ATTEMPTS:
        print("--- DECISION: FINISH ---")
        return END
    else:
        print("--- DECISION: RETRY ---")
        return "generate_code"


# ============================================================
# Build & Compile Graph
# ============================================================

graph = StateGraph(CodeGenState)

graph.add_node("generate_code", generate_code)
graph.add_node("check_code", check_code_execution)

graph.set_entry_point("generate_code")
graph.add_edge("generate_code", "check_code")
graph.add_conditional_edges(
    "check_code",
    decide_next,
    ["generate_code", END]
)

coder_agent = graph.compile()


# ============================================================
# Runner Utility
# ============================================================

def call_reflection_coding_agent(agent, prompt, verbose=False):
    events = agent.stream(
        {
            "messages": [HumanMessage(content=prompt)],
            "attempts": 0,
            "error_flag": "unknown",
        },
        stream_mode="values",
    )

    print("Running Agent...\n")

    for event in events:
        if verbose:
            event["messages"][-1].pretty_print()

    final_solution = event["code_solution"]

    print("\n\nFinal Solution")
    print("=" * 40)
    print("\nDescription:\n", final_solution.prefix)
    print("\nImports:\n", final_solution.imports)
    print("\nCode:\n", final_solution.code)


# ============================================================
# Example Run
# ============================================================

if __name__ == "__main__":
    # prompt = "write some code to demonstrate how to do a pivot table in pandas"
    prompt = input("Enter your Question: ")
    call_reflection_coding_agent(coder_agent, prompt, verbose=True)
