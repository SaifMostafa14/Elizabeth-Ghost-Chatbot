# Elizabeth Ghost Chatbot

This repository contains two approaches for a library chatbot project. The original prototype used **Rasa** for intent recognition and dialogue management, while the final solution relies on **OpenAI** language models.

The codebase is now organised into two directories:

- [`rasa/`](rasa/) – the historical Rasa project
- [`openai/`](openai/) – the active OpenAI implementation

## Rasa prototype

The directory [`rasa/`](rasa/) contains the remains of an early experiment using [Rasa](https://rasa.com/). That prototype is no longer actively maintained, but the configuration and training data remain for reference.

## Final project: OpenAI implementation

The completed implementation lives entirely in the [`openai/`](openai/) directory. The core entry point is `openai/main.py`, which launches a command line assistant powered by OpenAI's API. The chatbot classifies user intents using a prompt template and responds with generated text.

### Requirements

* Python 3.8+
* An OpenAI API key

Install the Python dependencies (for example via `pip install openai selenium`). Selenium is only required if you enable the optional web‑scraping functions.

### Running

1. Set your OpenAI credentials in the environment:

   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

2. Run the assistant:

   ```bash
   python openai/main.py
   ```

The script will greet you and wait for your questions. Type `stop`, `quit` or `exit` to end the session.
