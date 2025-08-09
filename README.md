# `#BuildWithPuch`

# 🧠 Groq AI Knowledge, Document Q&A & Health Assistant MCP

This is a Modular Conversational Platform (MCP) powered by **FastMCP**, **Groq LLaMA 3.1 (8B)** via `ChatGroq`, and integrated with document parsing, health tools, and AI assistants for various domains including:

- ✅ Health checks
- 📄 Document Q&A (PDF/DOCX)
- 📘 Knowledge Assistant
- 🥗 Diet & Nutrition
- 🧠 Mental Health Support
- 🚨 Emergency Instructions
- 🏋️‍♂️ Exercise & Fitness Guidance

---

## 🚀 Features

- ✅ AI-generated health responses with safety disclaimers.
- 📄 Upload and query documents (PDF, DOCX) in natural language.
- 🔍 Ask general knowledge questions.
- 🧘 Mental health and emotional support.
- 🥗 Nutrition tips and diet planning.
- 🆘 First-aid emergency response instructions.
- 🏃‍♂️ Exercise and fitness recommendations.
- 🧩 Modular design with clean prompt builders and async tools.

---

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/GVKarthik-dev/MCP-PuchAI-Hackathon.git
cd MCP-PuchAI-Hackathon
````

### 2. Install dependencies

> **Note:** Make sure Python 3.9+ is installed & Install [uv](https://docs.astral.sh/uv/)

```bash
uv sync
```

### 3. Create Environment File

Create a `.env` file in the root directory with your **Groq API key** and any other required secrets:

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

### 4. Run the server

```bash
uv run python Server.py
```

The server will start at:
**[http://localhost:8000](http://localhost:8000)**

---

## 🧰 Tools Overview

| Tool                     | Description                                                   |
| ------------------------ | ------------------------------------------------------------- |
| `health_check`           | Answers user health queries.                                  |
| `upload_and_qa`          | Parses uploaded documents and answers questions contextually. |
| `ask_knowledge`          | Provides detailed explanations of any topic.                  |
| `diet_and_nutrition`     | Offers advice and tips on nutrition and healthy eating.       |
| `mental_health_support`  | Responds with emotional support and coping strategies.        |
| `emergency_instructions` | Gives step-by-step first-aid guidance for emergencies.        |
| `exercise_and_fitness`   | Provides fitness recommendations and recovery tips.           |

---

## 🧱 Tech Stack

* **[FastMCP](https://github.com/eunomia-engineering/fastmcp)** - Modular conversational framework
* **[ChatGroq](https://pypi.org/project/langchain-groq/)** - Integration with Groq's blazing fast LLaMA 3.1 models
* **`pdfplumber`** - Extracts text from PDFs
* **`python-docx`** - Reads `.docx` documents
* **`dotenv`** - Loads environment variables
* **`eunomia_mcp`** - Eunomia policy-based middleware

---

## 🧪 Example Usage

### Health Question

```json
{
  "tool": "health_check",
  "query": "What should I do if I have a mild fever?"
}
```

### Document Q\&A

```json
{
  "tool": "upload_and_qa",
  "doc_base64": "<base64-encoded-pdf-or-docx>",
  "question": "What are the main responsibilities of the company mentioned?",
  "file_type": "pdf"
}
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---

## ⚠️ Disclaimers

* The health and mental support information is **not** a replacement for professional medical advice.
* Emergency instructions are intended for first-aid and awareness, not as certified training.

---

## 🧩 Customization

You can add more tools or prompts by extending:

* Prompt builders (functions like `build_*_prompt`)
* Tool functions (`@mcp.tool`)

All prompt generation is modular and easy to modify.

---

## 👨‍💻 Author

Developed with ❤️ using FastMCP and Groq LLMs.
