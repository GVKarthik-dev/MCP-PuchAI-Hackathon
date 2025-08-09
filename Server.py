import os
import io
import base64
from typing import Optional
from dotenv import load_dotenv

import pdfplumber
from docx import Document

from fastmcp import FastMCP
from langchain_groq import ChatGroq

load_dotenv('.env')

mcp = FastMCP(name="Groq AI Knowledge, Document Q&A & Health Assistant")


chat_groq = ChatGroq(
    model='llama-3.1-8b-instant',
    max_tokens=250,
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
        ""
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
async def diet_and_nutrition(query: str) -> str:
    """
    Diet and Nutrition Assistant:
    Provide personalized diet plans, nutritional info, and healthy eating tips.
    """
    prompt = (
        "You are a helpful diet and nutrition expert.\n"
        "Give recommendations on diet plans, nutritional advice, and healthy eating tailored to the user's query.\n"
        "Include practical tips and friendly encouragement.\n\n"
        f"User query: {query}"
    )
    try:
        response = await chat_groq.ainvoke(prompt)
        return response.content
    except Exception as e:
        return f"Error generating diet and nutrition advice: {e}"

@mcp.tool
async def mental_health_support(query: str) -> str:
    """
    Mental Health Support:
    Offer empathetic responses, coping strategies, and resources for mental well-being and stress management.
    Always include encouragement to seek professional help if needed.
    """
    prompt = (
        "You are a compassionate mental health assistant.\n"
        "Respond empathetically, provide coping strategies, and helpful resources.\n"
        "Encourage the user to consult a mental health professional if needed.\n\n"
        f"User query: {query}"
    )
    try:
        response = await chat_groq.ainvoke(prompt)
        return (
            "⚠️ Disclaimer: This advice is not a substitute for professional mental health support.\n\n"
            + response.content
        )
    except Exception as e:
        return f"Error generating mental health support: {e}"

@mcp.tool
async def emergency_instructions(emergency_type: str) -> str:
    """
    Emergency Instructions Tool:
    Provide clear, immediate, step-by-step advice for common emergencies such as choking or burns.
    Always includes safety precautions and a disclaimer to seek professional medical help urgently.
    """
    prompt = (
        "You are an expert emergency responder providing clear and concise instructions.\n"
        "Given the type of emergency provided, give step-by-step guidance on what to do immediately.\n"
        "Include safety precautions and remind the user to call emergency services if needed.\n\n"
        f"Emergency type: {emergency_type}\n"
        "Please provide instructions suitable for a layperson to follow."
    )
    try:
        response = await chat_groq.ainvoke(prompt)
        return (
            "⚠️ Emergency Disclaimer: These instructions are for immediate first aid only. "
            "Always call emergency services or seek professional medical help immediately in any serious emergency.\n\n"
            + response.content
        )
    except Exception as e:
        return f"Error generating emergency instructions: {e}"

@mcp.tool
async def exercise_and_fitness(query: str) -> str:
    """
    Exercise & Fitness Guide:
    Suggest exercises, fitness routines, and recovery tips based on user needs and input.
    Provide safe and practical recommendations.
    """
    prompt = (
        "You are a knowledgeable fitness coach.\n"
        "Suggest suitable exercises, workout routines, and recovery advice based on the user's input.\n"
        "Mention any necessary precautions.\n\n"
        f"User query: {query}"
    )
    try:
        response = await chat_groq.ainvoke(prompt)
        return response.content
    except Exception as e:
        return f"Error generating exercise and fitness advice: {e}"

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

        max_chars = 3000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n... (truncated)"

    except Exception as e:
        return f"Failed to extract text from document: {e}"

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
    mcp.run(transport="http", port=8000)
