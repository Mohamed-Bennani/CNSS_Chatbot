from flask import Flask, render_template, request, jsonify, Response
from llama_index.llms.ollama import Ollama
from llama_index.core import SimpleDirectoryReader
from llama_index.core.embeddings import resolve_embed_model
from llama_parse import LlamaParse
import faiss
import numpy as np
from dotenv import load_dotenv
import os
import requests
import re

load_dotenv()
app = Flask(__name__)

# Initialize models and load documents
llm = Ollama(model="mistral", request_timeout=800.0)
embed_model = resolve_embed_model("local:BAAI/bge-m3")

# Set up document parsing
parser = LlamaParse(result_type="markdown")
file_extractor = {".pdf": parser}
documents = SimpleDirectoryReader("./data", file_extractor=file_extractor).load_data()

# Function to chunk documents and handle mixed content
def process_document(document):
    chunks = []
    # Split the document into sections
    sections = re.split(r'\n\s*\n', document)
    for section in sections:
        if re.match(r'^(QUESTION|Q:)', section, re.IGNORECASE):
            # Handle Q&A format
            chunks.append(section.strip())
        elif len(section.split()) > 50:  # For longer sections
            # Split into smaller chunks
            sentences = re.split(r'(?<=[.!?])\s+', section)
            current_chunk = []
            current_length = 0
            for sentence in sentences:
                if current_length + len(sentence.split()) > 100:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_length = len(sentence.split())
                else:
                    current_chunk.append(sentence)
                    current_length += len(sentence.split())
            if current_chunk:
                chunks.append(' '.join(current_chunk))
        else:
            # Keep short sections as is
            chunks.append(section.strip())
    return chunks

# Embed and store chunks in FAISS
embeddings = []
chunks = []
for doc in documents:
    doc_chunks = process_document(doc.text)
    for chunk in doc_chunks:
        embedding = embed_model.get_text_embedding(chunk)
        embeddings.append(embedding)
        chunks.append(chunk)

embeddings = np.array(embeddings).astype('float32')
faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
faiss_index.add(embeddings)

def is_greeting(message):
    greetings = ['bonjour', 'salut', 'hello', 'hey', 'comment ça va', 'comment allez-vous']
    return any(greeting in message.lower() for greeting in greetings)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form['user_message']
    
    if is_greeting(user_message):
        greeting_response = "Bonjour ! Je suis un assistant virtuel spécialisé dans la CNSS au Maroc. Comment puis-je vous aider aujourd'hui avec des informations sur la CNSS ?"
        return jsonify({'bot_response': greeting_response})
    
    user_embedding = embed_model.get_text_embedding(user_message)
    
    # Retrieve relevant chunks
    k = 3  # Number of relevant chunks to retrieve
    _, indices = faiss_index.search(np.array([user_embedding]), k)
    relevant_chunks = [chunks[i] for i in indices[0]]
    
    # Construct prompt with relevant context
    context = "\n\n".join(relevant_chunks)
    prompt = f"""Vous êtes un assistant spécialisé dans la CNSS au Maroc. Votre rôle principal est d'assister les utilisateurs dans l'analyse des documents de la Caisse Nationale de Sécurité Sociale (CNSS) au Maroc. 
Vous devez être en mesure de répondre aux questions sur la CNSS en utilisant le contexte fourni. Le contexte peut contenir divers formats, y compris des questions-réponses, des explications détaillées et des guides étape par étape.

Si la question de l'utilisateur n'est pas liée à la CNSS, répondez poliment que vous êtes spécialisé dans la CNSS et demandez si vous pouvez les aider avec des informations sur ce sujet.

Contexte :
{context}

Question de l'utilisateur : {user_message}

Réponse :"""
    
    # Send request to Ollama API with streaming
    try:
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "mistral",
            "prompt": prompt,
            "stream": True
        }, stream=True, timeout=(30, None))
        
        def generate_stream():
            for line in response.iter_lines():
                if line:
                    yield f"data: {line.decode('utf-8')}\n\n"
        
        return Response(generate_stream(), content_type='text/event-stream')
    
    except requests.exceptions.Timeout:
        return jsonify({'bot_response': "La requête a expiré. Veuillez réessayer plus tard."})
    except Exception as e:
        return jsonify({'bot_response': "Une erreur s'est produite lors de la génération de la réponse."})

if __name__ == '__main__':
    app.run(debug=True)