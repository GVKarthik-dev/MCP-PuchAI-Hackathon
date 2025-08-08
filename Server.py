import os
import io
import base64
from typing import Optional
from dotenv import load_dotenv

import pdfplumber
from docx import Document

from fastmcp import FastMCP
from langchain_groq import ChatGroq

# Load environment variables from .env file
load_dotenv('.env.dev')

# Initialize FastMCP server
mcp = FastMCP(name="Groq AI Knowledge, Document Q&A & Health Assistant")

# Get Groq API key from environment, raise error if not found
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Please set GROQ_API_KEY in your environment variables.")

# Initialize ChatGroq client with your Groq API key
chat_groq = ChatGroq(
    model='llama-3.1-8b-instant',
    max_tokens=200,
    api_key=groq_api_key  # Pass the API key here if required by ChatGroq
)


@mcp.tool
async def health_check(query: str) -> str:
    """
    Health-related tool:
    Answer health queries with disclaimers using ChatGroq.
    Provides a summary of the situation and advises what steps to take.
    """
    prompt = (
        "You are an AI assistant specialized in health information. "
        "Please provide helpful and accurate answers, and include a concise summary of the situation "
        "and clear recommendations on what the user should do next. Always remind users to consult a healthcare professional.\n"
        f"User query: {query}"
    )

    try:
        response = await chat_groq.ainvoke(prompt)
        return (
            "Disclaimer: This is AI-generated information and not a substitute for professional medical advice.\n\n"
            + response.content
        )
    except Exception as e:
        return f"Failed to get response from ChatGroq: {e}"

@mcp.tool
async def ask_knowledge(question: str) -> str:
    """
    AI-Powered Knowledge Assistant:
    Generate in-depth explanations, summaries, or definitions on any topic.
    """
    prompt = f"Explain the following in detail:\n{question}"
    try:
        response = await chat_groq.ainvoke(prompt)
        return response.content
    except Exception as e:
        return f"Error getting response from ChatGroq: {e}"


@mcp.tool
async def upload_and_qa(
    doc_base64: str,
    question: str,
    file_type: Optional[str] = None  # 'pdf' or 'docx'
) -> str:
    """
    Contextual Document Q&A:
    Parse uploaded base64-encoded document (PDF or DOCX)
    and answer the question based on document content using ChatGroq.
    """
    # Decode base64 document
    try:
        decoded_bytes = base64.b64decode(doc_base64)
    except Exception as e:
        return f"Failed to decode base64 document: {e}"

    # Auto detect file type if not provided
    if file_type is None:
        if decoded_bytes.startswith(b'%PDF'):
            file_type = 'pdf'
        elif decoded_bytes.startswith(b'PK'):
            file_type = 'docx'
        else:
            return "Unsupported or unknown document format. Please specify 'file_type'."

    # Extract text from document
    text = ""
    try:
        if file_type == 'pdf':
            with pdfplumber.open(io.BytesIO(decoded_bytes)) as pdf:
                pages_text = [page.extract_text() or "" for page in pdf.pages]
                text = "\n".join(pages_text).strip()
        elif file_type == 'docx':
            with io.BytesIO(decoded_bytes) as f:
                doc = Document(f)
                paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
                text = "\n".join(paragraphs).strip()
        else:
            return "Unsupported file type. Supported types: 'pdf', 'docx'."

        if not text:
            return "Could not extract any text from the document."

        # Truncate text if too large to avoid prompt size issues
        max_chars = 3000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n... (truncated)"

    except Exception as e:
        return f"Failed to extract text from document: {e}"

    # Construct prompt for ChatGroq
    prompt = (
        "You are provided context extracted from a user-uploaded document.\n"
        f"Document content:\n{text}\n\n"
        f"Based on the above document, answer the following question:\n{question}"
    )

    try:
        response = await chat_groq.ainvoke(prompt)
        return response.content
    except Exception as e:
        return f"Failed to get response from ChatGroq: {e}"






if __name__ == "__main__":
    # Run MCP server with HTTP transport on port 8000
    mcp.run(transport="http", port=8000)
