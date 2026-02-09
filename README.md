# 🚀 AI Code Generator

A production-ready, self-correcting code generation web application powered by **LangGraph** and **local LLMs**. Features a modern **Gradio** interface with real-time streaming updates.

![Screenshot](./screenshot.png)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Gradio](https://img.shields.io/badge/gradio-5.0+-orange.svg)

## ✨ Features

- 🤖 **Self-Correcting Agent**: Automatically validates and fixes generated code up to 3 attempts
- ⚡ **Real-time Streaming**: Live status updates and code streaming
- 🎨 **Clean UI**: User-friendly Gradio interface with chat and code display
- 🔄 **Retry Logic**: Intelligent error handling and code refinement
- 📦 **Easy Deploy**: Simple setup with conda environment management

## 🏗️ Architecture

```
┌─────────────────┐      Stream       ┌─────────────────┐
│    Gradio UI    │ ◄────────────────►│  Agent Workflow │
│ (gradio_app.py) │                   │ (LangGraph/Py)  │
└─────────────────┘                   └────────┬────────┘
                                               │
                                               ▼
                                      ┌─────────────────┐
                                      │  vLLM Server    │
                                      │   (Port 5005)   │
                                      └─────────────────┘
```

## 📋 Prerequisites

- **Python 3.10+** with conda
- **vLLM server** running locally (see setup below)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd code-generator
```

### 2. Set Up vLLM Server

First, start your vLLM server with the model:

```bash
# In a separate terminal
conda create -n vllm_oss python=3.10 -y
conda activate vllm_oss
pip install vllm

# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
  --port=5005 \
  --model openai/gpt-oss-20b
```

### 3. Run the Application

The `start.sh` script handles dependency installation and starting the app.

```bash
# Make the script executable if needed
chmod +x start.sh

# Run the start script
./start.sh
```

The application will be available at `http://localhost:7860`

## 💻 Usage

1. **Open your browser** to `http://localhost:7860`
2. **Enter a prompt** describing the code you want (e.g., "write a function to calculate fibonacci numbers")
3. **Click "Submit"**
4. **Watch the magic**: See real-time status updates as the agent generates and validates code
5. **View Results**: The generated code will appear in the code block on the right

### Example Prompts

```
write a function to calculate fibonacci numbers recursively

create a pandas dataframe and perform a pivot table operation

implement a binary search tree with insert and search methods

write a decorator to measure function execution time
```

## 📁 Project Structure

```
code-generator/
├── backend/
│   ├── coder.py             # LangGraph agent workflow
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment configuration
├── gradio_app.py            # Main Gradio application
├── start.sh                 # Quick start script
├── stop.sh                  # Stop script
├── requirements.txt         # Project dependencies
└── README.md
```

## � Stopping the App

To stop the application and clean up processes:

```bash
./stop.sh
```

## 🔧 API & Customization

### Change vLLM Model

Edit `backend/coder.py`:

```python
def get_llm():
    return ChatOpenAI(
        model="your-model-name",  # Change this
        base_url="http://localhost:5005/v1",
        # ...
    )
```

## 🐛 Troubleshooting

### Application won't start
- **Check vLLM server**: Ensure vLLM is running on port 5005
- **Check dependencies**: Run `pip install -r requirements.txt` manually
- **Check logs**: Look at `app.log` for error messages

## 📝 License

MIT License - feel free to use this project for any purpose.

## 🙏 Acknowledgments

- **LangGraph** for the agent workflow framework
- **Gradio** for the web interface
- **vLLM** for local LLM inference
