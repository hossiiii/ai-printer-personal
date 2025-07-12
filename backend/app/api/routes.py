"""
API Routes for AI Printer
Voice-to-document generation endpoints
"""
import logging
import tempfile
import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from ..models.audio import (
    AudioUploadRequest, TranscriptionResponse, DocumentGenerationRequest, 
    DocumentResponse, RevisionRequest, PDFGenerationRequest, PDFGenerationResponse,
    ErrorResponse
)
from ..services.openai_service import get_openai_service, OpenAIService
from ..services.pdf_service import get_pdf_service, PDFService
from ..services.drive_service import get_drive_service, DriveService
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# File upload validation
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".webm"}
MAX_FILE_SIZE = settings.MAX_AUDIO_FILE_SIZE

def validate_audio_file(file: UploadFile) -> None:
    """Validate uploaded audio file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (this is approximate, actual size checked later)
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Transcribe uploaded audio file using OpenAI Whisper API
    
    Args:
        file: Audio file (WAV, MP3, M4A, WebM)
        language: Language code (optional, auto-detect if None)
        
    Returns:
        TranscriptionResponse with transcribed text and metadata
    """
    try:
        logger.info(f"Received transcription request: filename={file.filename}, content_type={file.content_type}")
        
        # Validate file
        validate_audio_file(file)
        
        # Read file content
        audio_data = await file.read()
        
        # Check actual file size
        if len(audio_data) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large: {len(audio_data)} bytes. Maximum: {MAX_FILE_SIZE} bytes"
            )
        
        logger.info(f"Transcribing audio file: {file.filename} ({len(audio_data)} bytes)")
        
        # Transcribe audio
        result = await openai_service.transcribe_audio(audio_data, language)
        
        logger.info(f"Transcription completed: {result.text[:100]}...")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/generate-document", response_model=DocumentResponse)
async def generate_document(
    request: DocumentGenerationRequest,
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Generate document content from transcription using OpenAI GPT API
    
    Args:
        request: Document generation request with transcription and options
        
    Returns:
        DocumentResponse with HTML/CSS content and metadata
    """
    try:
        logger.info(f"Generating document from transcription: {request.transcription[:100]}...")
        
        # Generate document
        result = await openai_service.generate_document(
            transcription=request.transcription,
            document_type=request.document_type,
            custom_instructions=request.custom_instructions
        )
        
        logger.info(f"Document generated: {result.document_type} - {result.title}")
        return result
        
    except Exception as e:
        logger.error(f"Document generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")

@router.post("/revise-document", response_model=DocumentResponse)
async def revise_document(
    request: RevisionRequest,
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Revise existing document based on voice or text instructions
    
    Args:
        request: Revision request with original content and instructions
        
    Returns:
        Updated DocumentResponse with revised content
    """
    try:
        logger.info(f"Revising document with instruction: {request.revision_instruction}")
        
        # For revision, we generate a new document with the revision context
        revision_transcription = f"Revise the following document: {request.revision_instruction}"
        
        result = await openai_service.generate_document(
            transcription=revision_transcription,
            custom_instructions=f"Original content: {request.original_content}"
        )
        
        logger.info(f"Document revised successfully")
        return result
        
    except Exception as e:
        logger.error(f"Document revision failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document revision failed: {str(e)}")

@router.post("/generate-pdf", response_model=PDFGenerationResponse)
async def generate_pdf(
    request: PDFGenerationRequest,
    background_tasks: BackgroundTasks,
    pdf_service: PDFService = Depends(get_pdf_service),
    drive_service: DriveService = Depends(get_drive_service)
):
    """
    Generate PDF from HTML/CSS content and optionally save to Google Drive
    
    Args:
        request: PDF generation request with content and options
        
    Returns:
        PDFGenerationResponse with file info and download links
    """
    try:
        logger.info(f"Generating PDF: {request.document_title}")
        
        # Generate PDF
        pdf_result = await pdf_service.generate_pdf(
            html_content=request.html_content,
            css_content=request.css_content,
            title=request.document_title
        )
        
        response = PDFGenerationResponse(
            success=True,
            filename=pdf_result["filename"],
            file_size=pdf_result["file_size"],
            file_path=pdf_result["file_path"] if settings.DEVELOPMENT else None
        )
        
        # Save to Google Drive if requested and not in development mode
        if request.save_to_drive and not settings.DEVELOPMENT:
            try:
                drive_link = await drive_service.upload_pdf(
                    file_path=pdf_result["file_path"],
                    filename=pdf_result["filename"],
                    document_type=request.document_type
                )
                response.drive_link = drive_link
                
                # Schedule cleanup of local file
                background_tasks.add_task(cleanup_temp_file, pdf_result["file_path"])
                
            except Exception as e:
                logger.warning(f"Failed to upload to Google Drive: {e}")
                # Continue without Drive upload
        
        logger.info(f"PDF generated successfully: {response.filename}")
        return response
        
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.get("/download/{filename}")
async def download_pdf(filename: str):
    """
    Download generated PDF file (development mode only)
    
    Args:
        filename: Name of the PDF file to download
        
    Returns:
        File download response
    """
    if not settings.DEVELOPMENT:
        raise HTTPException(status_code=404, detail="Downloads not available in production mode")
    
    try:
        # Construct file path (assuming PDFs are saved in temp directory)
        file_path = os.path.join(tempfile.gettempdir(), "ai-printer", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File download failed: {e}")
        raise HTTPException(status_code=500, detail="Download failed")

@router.post("/transcribe-and-generate", response_model=DocumentResponse)
async def transcribe_and_generate(
    file: UploadFile = File(...),
    document_type: Optional[str] = None,
    custom_instructions: Optional[str] = None,
    language: Optional[str] = None,
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Combined endpoint: transcribe audio and generate document in one step
    
    Args:
        file: Audio file to transcribe
        document_type: Type of document to generate
        custom_instructions: Additional instructions
        language: Audio language
        
    Returns:
        DocumentResponse with generated content
    """
    try:
        # Validate and transcribe audio
        validate_audio_file(file)
        audio_data = await file.read()
        
        if len(audio_data) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        
        logger.info(f"Processing audio-to-document for: {file.filename}")
        
        # Transcribe audio
        transcription = await openai_service.transcribe_audio(audio_data, language)
        
        # Generate document
        document = await openai_service.generate_document(
            transcription=transcription.text,
            document_type=document_type,
            custom_instructions=custom_instructions
        )
        
        logger.info(f"Complete workflow finished: {document.title}")
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio-to-document workflow failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")

# Utility functions
async def cleanup_temp_file(file_path: str):
    """Clean up temporary files"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temp file {file_path}: {e}")

# Health check for API routes
@router.get("/health")
async def api_health():
    """Health check for API routes"""
    return {"status": "healthy", "module": "api-routes"}