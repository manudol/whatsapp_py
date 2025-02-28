import numpy as np
from typing import List, Tuple
import textwrap
import json

from openai_client.client import client

class Rag:
    def __init__(self, chunk_size:int, file_path : str):
        self.embeddings = []
        self.chunks = []
        self.chunk_size = chunk_size
        self.file_path = file_path
        self.load_and_process_chunks()

    def load_and_process_chunks(self):
        # Read the text file
        thread = None
        
        with open(self.file_path, 'r') as f:
            thread = json.load(f)

        messages = thread['messages']
        text = ""

        for msg in messages:
            role = msg['role']
            content = msg['content']

            text += 'Message from '+role+":\n"
            text += content

        # Split text into chunks
        self.text_chunks = textwrap.wrap(text, 
                                         self.chunk_size, 
                                         break_long_words=False)
         # Create embeddings for each chunk
        for chunk in self.text_chunks:
            embedding = self.get_embedding(chunk)
            self.embeddings.append(embedding)

    def get_embedding(self, text: str) -> List[float]:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding

    
    def find_most_relevant_chunks(self, 
                                  query: str, 
                                  top_k: int = 2) -> List[Tuple[str, float]]:
        # Get query embedding
        query_embedding = self.get_embedding(query)

        # Calculate similarities
        similarities = []
        for idx, emb in enumerate(self.embeddings):
            similarity = np.dot(query_embedding, emb)
            similarities.append((self.text_chunks[idx], similarity))

        # Sort by similarity and return top k
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]


    def generate_response(self, query: str) -> str:
        # Find relevant chunks
        relevant_chunks = self.find_most_relevant_chunks(query)

        # Prepare context
        context = "\n".join([chunk[0] for chunk in relevant_chunks])

        # Create prompt
        prompt = f"###Relevant context from past messages: {context}\n\n###Question: {query}"

        return prompt
