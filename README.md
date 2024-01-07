

# NED University Admissions ChatBot

The university admission chatbot is a useful tool designed to provide assistance and information by answering general student queries during university admissions using state-of-the-art language models and vector stores.

## Prerequisites

Before you can start using the  ChatBot, make sure you have the following prerequisites installed on your system:

- Python 3.6 or higher
- Required Python packages (all packages are in requirement.txt)
    - langchain
    - chainlit
    - sentence-transformers
    - faiss
    - PyPDF2 (for PDF document loading)

## Installation

1. Clone this repository to your local machine.

2. Create a Python virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use: venv\Scripts\activate.bat
    ```

3. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Download the required language models and data. https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/blob/main/llama-2-7b-chat.ggmlv3.q8_0.bin

5. Put the model in the root folder.
