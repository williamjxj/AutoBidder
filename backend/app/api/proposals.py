from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from app.models.schemas import (
    ProposalRequest, ProposalResponse,
    AnalysisRequest, AnalysisResponse,
    DocumentUpload
)
from app.services.proposal_service import proposal_service
from app.services.vector_store import vector_store_service

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_job_requirements(request: AnalysisRequest):
    """Analyze job requirements and extract key information."""
    try:
        result = proposal_service.analyze_job_requirements(request.description)
        return AnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=ProposalResponse)
async def generate_proposal(request: ProposalRequest):
    """Generate a proposal for a job posting."""
    try:
        result = proposal_service.generate_proposal(
            job_title=request.job_requirement.title,
            job_description=request.job_requirement.description,
            requirements=request.job_requirement.requirements,
            user_profile=request.user_profile,
            custom_instructions=request.custom_instructions
        )
        return ProposalResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload documents to the knowledge base."""
    try:
        texts = []
        metadatas = []
        
        for file in files:
            content = await file.read()
            text = content.decode('utf-8')
            
            texts.append(text)
            metadatas.append({
                "source": file.filename,
                "type": "uploaded_document"
            })
        
        num_chunks = vector_store_service.add_documents(texts, metadatas)
        
        return {
            "message": f"Successfully uploaded {len(files)} files",
            "chunks_created": num_chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/add")
async def add_document_text(document: DocumentUpload):
    """Add a document to the knowledge base via text."""
    try:
        num_chunks = vector_store_service.add_documents(
            [document.content],
            [{"source": document.filename, "type": document.document_type}]
        )
        
        return {
            "message": "Document added successfully",
            "chunks_created": num_chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/clear")
async def clear_documents():
    """Clear all documents from the knowledge base."""
    try:
        vector_store_service.clear()
        return {"message": "Knowledge base cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
