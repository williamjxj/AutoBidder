# Quick Start Guide

## For Development

### 1. Clone the Repository
```bash
git clone https://github.com/williamjxj/auto-bidder-ai.git
cd auto-bidder-ai
```

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the server
cd app
python main.py
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup (in a new terminal)
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env.local file (already exists)
# Make sure it points to: NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Using Docker

### 1. Prerequisites
- Docker and Docker Compose installed

### 2. Setup
```bash
# Create .env file from example
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Build and run
docker-compose up --build
```

Access the application:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/api/v1/openapi.json`

## First Steps

1. **Open the application** at `http://localhost:3000`

2. **Enter job details**:
   - Job Title: e.g., "Full-Stack Developer"
   - Job Description: Paste the job posting

3. **Click "Analyze Job"** to extract requirements, technologies, and skills

4. **Click "Generate Proposal"** to create a customized proposal

5. **Review and customize** the generated proposal

6. **Copy to clipboard** and use it!

## Tips

- Add custom instructions to personalize proposals further
- Upload documents (resumes, portfolios) to enhance the RAG system
- The more context you provide, the better the proposals

## Troubleshooting

**Backend not starting?**
- Make sure you have set OPENAI_API_KEY in `.env`
- Check that all dependencies are installed
- Verify Python version is 3.9+

**Frontend not connecting to backend?**
- Ensure backend is running on port 8000
- Check NEXT_PUBLIC_API_URL in frontend/.env.local
- Verify CORS settings in backend/app/core/config.py

**API errors?**
- Check your OpenAI API key is valid
- Verify you have API credits
- Check the backend logs for detailed error messages
