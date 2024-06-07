

# NED University Admissions ChatBot

The university admission chatbot is a useful tool designed to provide assistance and information by answering general student queries during university admissions using state-of-the-art language models and vector stores.

## Prerequisites

Before you can start using the  ChatBot, make sure you have the following prerequisites installed on your system:

- Python 3.9 or higher
- Required Python packages (all packages are in requirement.txt)
    - langchain
    - faiss
    - PyPDF
    - google-generativeai
    - langchain_groq

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

4. Create .env file for creating environment variables.
5. Add your Google and Groq API key variable in the file. You can get your API key from here
- For Google API Key: https://makersuite.google.com/app/apikey
- For Groq API Key: https://console.groq.com/playground

    ```bash
    GOOGLE_API_KEY="Insert your google API key here"
    GROQ_API_KEY = 'Insert your Groq Api here'
    ```

## Run API on local server

1. Open cmd in the root folder and write this command to run the live server. 
    ```bash
    uvicorn main:app --reload
    ```
    
## API endpoints

- /docs -> You will see the automatic interactive API documentation
- /llm_on_cpu -> POST Method
