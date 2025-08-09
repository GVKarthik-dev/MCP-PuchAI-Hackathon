import io
import base64
from typing import Optional
from dotenv import load_dotenv

import pdfplumber
from docx import Document
from eunomia_mcp import create_eunomia_middleware
from fastmcp import FastMCP
from langchain_groq import ChatGroq

load_dotenv('.env')

mcp = FastMCP(name="Groq AI Knowledge, Document Q&A & Health Assistant")


chat_groq = ChatGroq(
    model='llama-3.1-8b-instant',
    max_tokens=250
)


# -----------------------------
# PROMPT BUILDERS
# -----------------------------


# @mcp.prompt
def ask_health_question(question: str) -> str:
    """
    Generates a health-related question prompt for ChatGroq.
    Keeps it short, clear, and ready to be passed to the AI.
    """
    return (
        "You are an AI assistant specialized in health information and a Good Doctor. "
        "Please provide helpful and accurate answers. "
        "Include less than 5 simple steps for handling the situation. "
        "Keep it short, direct, and clear.\n"
        f"User query: {question}"
    )

# @mcp.prompt
def build_knowledge_prompt(question: str) -> str:
    """
    Creates a detailed request prompt for the AI Knowledge Assistant.
    """
    return f"Explain the following in detail and provide clear, organized information:\n{question}"


# @mcp.prompt
def build_doc_qa_prompt(document_text: str, question: str) -> str:
    """
    Creates a contextual Q&A prompt based on document text.
    """
    return (
        "You are provided with content extracted from a user-uploaded document.\n"
        f"Document content:\n{document_text}\n\n"
        f"Based on the above, answer the following question clearly and concisely:\n{question}"
    )

# @mcp.prompt
def build_diet_and_nutrition_prompt(query: str) -> str:
    """
    Creates a user-friendly diet & nutrition prompt.
    """
    return (
        "You are a helpful diet and nutrition expert.\n"
        "Provide helpful and accurate answers in less than 6 steps, keeping it short and simple.\n"
        "Give recommendations on diet plans, nutritional advice, and healthy eating tailored to the user's query.\n"
        "Include practical tips and friendly encouragement.\n\n"
        f"User query: {query}"
    )

# @mcp.prompt
def build_mental_health_prompt(query: str) -> str:
    """
    Creates a compassionate mental health support prompt.
    """
    return (
        "You are a compassionate mental health assistant.\n"
        "Respond empathetically, provide coping strategies, and helpful resources.\n"
        "Encourage the user to consult a mental health professional if needed.\n\n"
        f"User query: {query}"
    )

# @mcp.prompt
def build_emergency_instructions_prompt(emergency_type: str) -> str:
    """
    Creates a clear emergency response prompt.
    """
    return (
        "You are an expert emergency responder providing clear and concise instructions.\n"
        "Given the type of emergency provided, give step-by-step guidance on what to do immediately.\n"
        "Include safety precautions and remind the user to call emergency services if needed.\n\n"
        f"Emergency type: {emergency_type}\n"
        "Please provide instructions suitable for a layperson to follow."
    )

# @mcp.prompt
def build_exercise_and_fitness_prompt(query: str) -> str:
    """
    Creates a fitness guidance prompt.
    """
    return (
        "You are a knowledgeable fitness coach.\n"
        "Suggest suitable exercises, workout routines, and recovery advice based on the user's input.\n"
        "Mention any necessary precautions.\n\n"
        f"User query: {query}")



# -----------------------------
# TOOLS
# -----------------------------


@mcp.tool
async def health_check(query: str) -> str:
    """
    Health-related tool:
    Answers health queries with disclaimers using ChatGroq.
    """
    try:
        ai_prompt = ask_health_question(query)

        response = await chat_groq.ainvoke(ai_prompt)

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
    prompt = build_knowledge_prompt(question)
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
    # Step 1 - Decode file
    try:
        decoded_bytes = base64.b64decode(doc_base64)
    except Exception as e:
        return f"Failed to decode base64 document: {e}"

    # Step 2 - Detect type
    if file_type is None:
        if decoded_bytes.startswith(b'%PDF'):
            file_type = 'pdf'
        elif decoded_bytes.startswith(b'PK'):
            file_type = 'docx'
        else:
            return "Unsupported or unknown document format. Please specify 'file_type'."

    # Step 3 - Extract text
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

        # Limit text for token efficiency
        max_chars = 3000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n... (truncated)"
    except Exception as e:
        return f"Failed to extract text from document: {e}"

    # Step 4 - Build prompt using @mcp.prompt
    prompt = build_doc_qa_prompt(text, question)

    # Step 5 - Get AI response
    try:
        response = await chat_groq.ainvoke(prompt)
        return response.content
    except Exception as e:
        return f"Failed to get response from ChatGroq: {e}"

@mcp.tool
async def diet_and_nutrition(query: str) -> str:
    try:
        prompt = build_diet_and_nutrition_prompt(query)
        response = await chat_groq.ainvoke(prompt)
        return response.content
    except Exception as e:
        return f"Error generating diet and nutrition advice: {e}"

@mcp.tool
async def mental_health_support(query: str) -> str:
    try:
        prompt = build_mental_health_prompt(query)
        response = await chat_groq.ainvoke(prompt)
        return (
            "⚠️ Disclaimer: This advice is not a substitute for professional mental health support.\n\n"
            + response.content
        )
    except Exception as e:
        return f"Error generating mental health support: {e}"

@mcp.tool
async def emergency_instructions(emergency_type: str) -> str:
    try:
        prompt = build_emergency_instructions_prompt(emergency_type)
        response = await chat_groq.ainvoke(prompt)
        return (
            "⚠️ Emergency Disclaimer: These instructions are for immediate first aid only. "
            "Always call emergency services or seek professional medical help immediately.\n\n"
            + response.content
        )
    except Exception as e:
        return f"Error generating emergency instructions: {e}"

@mcp.tool
async def exercise_and_fitness(query: str) -> str:
    try:
        prompt = build_exercise_and_fitness_prompt(query)
        response = await chat_groq.ainvoke(prompt)
        return response.content
    except Exception as e:
        return f"Error generating exercise and fitness advice: {e}"

middleware = create_eunomia_middleware(policy_file="mcp_policies.json")
mcp.add_middleware(middleware)



if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
