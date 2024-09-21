# CNSS_Chatbot
This project is a Flask-based chatbot that assists users with information related to the Caisse Nationale de Sécurité Sociale (CNSS) in Morocco. It uses Mistral language model for natural language understanding, document retrieval, and voice command support to enhance user interactions.
# Features
Natural Language Processing (NLP): The chatbot processes user input and generates relevant responses.
Voice Commands: Users can interact with the chatbot using voice commands, offering a hands-free experience.
Document Parsing: The system parses CNSS-related documents and processes them into smaller chunks for better information retrieval.
Embeddings & Search: Uses FAISS for fast search and embedding retrieval, allowing the chatbot to find relevant information from CNSS documents.
Contextual Responses: The chatbot leverages a prompt that includes relevant context from the CNSS documents to answer user queries accurately.
# Tech Stack
Flask: Web framework used to serve the chatbot locally.
Mistral Model (via Ollama API): Provides the language model used to generate responses.
FAISS: For efficient similarity search on embedded document chunks.
LlamaParse: A custom parser used to process and chunk CNSS documents.
NumPy: For handling embeddings as numeric arrays.

# Installation
Clone the repository



Set up a virtual environment (optional but recommended):


python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install the required dependencies:


pip install -r requirements.txt

Create a .env file in the root of your project and add your LLAMA_CLOUD_API_KEY:

LLAMA_CLOUD_API_KEY="your-llama-api-key-here"

Make sure you have the Mistral model running locally via Ollama and the required CNSS documents in the ./data directory.

Run the Flask app:


App.py

-Open your browser and go to http://127.0.0.1:5000/ to interact with the chatbot.

# Usage
The chatbot can answer questions related to CNSS in Morocco.
It retrieves relevant chunks from CNSS documents, embedding them using a local embedding model.
It supports voice commands, allowing users to speak their queries instead of typing.

# Example Queries

"Qu'est-ce que la CNSS ?"

"Comment fonctionne la sécurité sociale au Maroc ?"

"Quels sont les documents requis pour l'inscription à la CNSS ?"

# Chatbot Interface Overview
![Screen](https://github.com/user-attachments/assets/eff438cb-9794-4879-a541-00b47ee67770)
