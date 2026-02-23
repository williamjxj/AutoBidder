# Auto-Bidder Backend (Python AI Service)

Python FastAPI service powering AI features: RAG knowledge base, proposal generation, and job scraping.

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Vector DB**: ChromaDB 0.4+
- **RAG**: LangChain 0.1+
- **LLM**: OpenAI GPT-4-turbo
- **Embeddings**: OpenAI text-embedding-3-small
- **Scraping**: Crawlee (Python)
- **Document Processing**: pypdf, python-docx

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Lint and format
ruff check .
black .
```

## Environment Variables

See `.env.example` for required configuration.

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── main.py              # FastAPI entry point
├── config.py            # Environment configuration
├── routers/             # API route handlers
├── services/            # Business logic
├── models/              # Pydantic schemas
└── core/                # Core utilities
```

## Development

See [auto-bidder/docs/quickstart.md](../docs/quickstart.md) for detailed setup instructions.
