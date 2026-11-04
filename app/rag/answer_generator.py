from dotenv import load_dotenv
from google import genai
from google.genai import types
import os

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

# building context for LLM --> formatting retrieved chunks
def build_context(retrieved_chunks):
    context_parts = []

    for chunk in retrieved_chunks:
        source = chunk['source']
        page_number = chunk['page_number']
        text = chunk['text']

        # Format the source, page number, and text
        formatted = f'Source: {source}\nPage: {page_number}\nContent: {text}'

        # Append the formatted passage to context_parts
        context_parts.append(formatted)

    return "\n\n".join(context_parts)

# test
# test at retriever

SYSTEM_PROMPT = """
You are FactoryMind's maintenance documentation assistant.

# Add your instructions here.
1. Answer using only the retrieved maintenance passages as factual support.
2. Cite the document filename and PDF page number.
3. Preserve relevant electrical and maintenance safety warnings.
4. State when the provided context doesn't contain sufficient information.
5. Never present a possible cause as a confirmed diagnosis.
"""

def generate_answer(question: str, retrieved_chunks: list):
    if not retrieved_chunks:
        return 'No relevant maintenance info found' #--> saves unnecessary API Calls
    
    context = build_context(retrieved_chunks)

    # Construct system and user messages
    user_prompt = f'''
        Question: 
        {question}
    
        Retrieved Maintenance documentation: 
        {context}
        '''
    
    # Call the selected LLM
    response = client.models.generate_content(
        model = 'gemini-3.5-flash-lite',
        contents = user_prompt,
        config = types.GenerateContentConfig(
            system_instruction= SYSTEM_PROMPT,
            temperature = 0.2

        )
    )
    # Return the generated answer
    return response.text