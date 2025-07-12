"""
Audio processing data models
Defines request/response schemas for voice-to-document workflow
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, Dict, Any
from datetime import datetime

class AudioUploadRequest(BaseModel):
    """Request model for audio file upload"""
    language: Optional[str] = Field(default="auto", description="Audio language (auto-detect if not specified)")
    enhance_quality: bool = Field(default=True, description="Apply audio enhancement")
    
class TranscriptionResponse(BaseModel):
    """Response model for audio transcription"""
    text: str = Field(..., description="Transcribed text from audio")
    language: str = Field(..., description="Detected or specified language")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Transcription confidence score")
    duration: float = Field(..., description="Audio duration in seconds")
    processing_time: float = Field(..., description="Processing time in seconds")
    
class DocumentGenerationRequest(BaseModel):
    """Request model for document generation from transcription"""
    transcription: str = Field(..., min_length=1, description="Source transcription text")
    document_type: Optional[Literal["flyer", "announcement", "notice", "event"]] = Field(
        default=None, 
        description="Document type (auto-detected if not specified)"
    )
    custom_instructions: Optional[str] = Field(
        default=None,
        description="Additional instructions for document generation"
    )
    
    @validator('transcription')
    def validate_transcription(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Transcription too short')
        return v.strip()

class DocumentResponse(BaseModel):
    """Response model for generated document"""
    html_content: str = Field(..., description="Generated HTML content")
    css_content: str = Field(..., description="Generated CSS styling")
    document_type: str = Field(..., description="Determined document type")
    title: str = Field(..., description="Document title")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    
class RevisionRequest(BaseModel):
    """Request model for document revision"""
    original_content: Dict[str, Any] = Field(..., description="Original document content")
    revision_instruction: str = Field(..., min_length=3, description="Revision instructions")
    revision_type: Literal["voice", "text"] = Field(default="voice", description="Type of revision input")

class PDFGenerationRequest(BaseModel):
    """Request model for PDF generation"""
    html_content: str = Field(..., description="HTML content to convert")
    css_content: str = Field(..., description="CSS styling to apply")
    document_title: str = Field(..., description="Document title for filename")
    save_to_drive: bool = Field(default=True, description="Save to Google Drive")
    document_type: str = Field(..., description="Document type for folder organization")

class PDFGenerationResponse(BaseModel):
    """Response model for PDF generation"""
    success: bool = Field(..., description="Generation success status")
    file_path: Optional[str] = Field(None, description="Local file path (development mode)")
    drive_link: Optional[str] = Field(None, description="Google Drive link (production mode)")
    filename: str = Field(..., description="Generated filename")
    file_size: int = Field(..., description="File size in bytes")

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
