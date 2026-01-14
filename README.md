# Auto Bidder AI

AI-powered proposal automation agent. Seamlessly integrates job scraping, requirement analysis, and personalized proposal drafting into a high-speed workflow.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  React Components + Tailwind CSS + shadcn/ui        │   │
│  │  - ProposalGenerator                                 │   │
│  │  - Job Analysis Display                             │   │
│  │  - Proposal Editor                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  API Endpoints  │→ │   Services   │→ │  AI Models   │  │
│  │  - Analyze      │  │  - Proposal  │  │  - LangChain │  │
│  │  - Generate     │  │  - Vector    │  │  - OpenAI    │  │
│  │  - Documents    │  │  - Llama     │  │              │  │
│  └─────────────────┘  └──────────────┘  └──────────────┘  │
│                              ↕                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Vector Store (ChromaDB)                    │    │
│  │         - Document Embeddings                      │    │
│  │         - RAG Context Retrieval                    │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **LangChain** - Framework for developing applications powered by language models
- **Llama-index** - Data framework for LLM applications
- **RAG (Retrieval Augmented Generation)** - Enhanced AI responses using knowledge base
- **ChromaDB** - Vector database for embeddings
- **OpenAI** - Language model provider

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful, accessible UI components

## 📋 Features

- 🤖 **AI-Powered Job Analysis** - Automatically extract key requirements, technologies, and skills from job postings
- ✍️ **Proposal Generation** - Generate personalized, professional proposals using AI
- 📚 **RAG Knowledge Base** - Upload documents to enhance proposal quality with relevant context
- 🎯 **Match Scoring** - Get estimated match scores for job requirements
- 💡 **Smart Suggestions** - Receive AI-powered suggestions to improve proposals
- 🎨 **Modern UI** - Clean, responsive interface built with Next.js and Tailwind CSS

## 🛠️ Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
```bash
cp .env.example .env
```

5. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your-api-key-here
```

6. Run the backend server:
```bash
cd app
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file from the example:
```bash
cp .env.local.example .env.local
```

4. Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## 📖 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/api/v1/openapi.json`
- Health Check: `http://localhost:8000/health`

### Key Endpoints

#### Analyze Job Requirements
```http
POST /api/v1/proposals/analyze
Content-Type: application/json

{
  "description": "Job description text..."
}
```

#### Generate Proposal
```http
POST /api/v1/proposals/generate
Content-Type: application/json

{
  "job_requirement": {
    "title": "Full-Stack Developer",
    "description": "Job description...",
    "requirements": ["React", "Node.js"]
  },
  "custom_instructions": "Optional custom instructions..."
}
```

#### Upload Documents to Knowledge Base
```http
POST /api/v1/proposals/documents/upload
Content-Type: multipart/form-data

files: [file1.txt, file2.txt]
```

## 🔧 Configuration

### Backend Configuration (`backend/.env`)

```env
OPENAI_API_KEY=your-api-key-here
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
CHROMA_PERSIST_DIR=./data/chroma
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Frontend Configuration (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🎯 Usage

1. **Enter Job Information**: Paste the job title and description
2. **Analyze Requirements**: Click "Analyze Job" to extract key information
3. **Generate Proposal**: Click "Generate Proposal" to create a customized proposal
4. **Review & Customize**: Review the generated proposal and suggestions
5. **Copy & Use**: Copy the proposal to your clipboard and use it

## 🧪 Development

### Backend Structure
```
backend/
├── app/
│   ├── api/           # API routes
│   ├── core/          # Configuration
│   ├── models/        # Data models
│   ├── services/      # Business logic
│   └── main.py        # Application entry point
└── requirements.txt   # Python dependencies
```

### Frontend Structure
```
frontend/
├── app/               # Next.js app directory
├── components/        # React components
│   └── ui/           # shadcn/ui components
└── lib/              # Utility functions
```

## 📝 License

MIT

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Llama-index Documentation](https://docs.llamaindex.ai/)
- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com/)

