"""
Database models for AI Printer
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
import enum
from .connection import Base


class DocumentType(enum.Enum):
    MEETING_MINUTES = "meeting_minutes"
    LETTER = "letter"
    REPORT = "report"
    ANNOUNCEMENT = "announcement"
    FLYER = "flyer"
    CUSTOM = "custom"


class DocumentStatus(enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class UserRole(enum.Enum):
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


class User(Base):
    """User model with authentication and subscription info"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    
    # Subscription info
    subscription_tier = Column(String(50), default="free")
    subscription_expires = Column(DateTime(timezone=True))
    monthly_usage = Column(Integer, default=0)
    monthly_limit = Column(Integer, default=100)
    
    # Google Drive integration
    google_refresh_token = Column(Text)
    google_drive_folder_id = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    templates = relationship("Template", back_populates="user", cascade="all, delete-orphan")
    usage_stats = relationship("UsageStats", back_populates="user", cascade="all, delete-orphan")


class Template(Base):
    """Document templates for different document types"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    document_type = Column(Enum(DocumentType), nullable=False)
    template_content = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Template metadata
    variables = Column(JSON)  # List of variables that can be replaced
    style_settings = Column(JSON)  # Font, color, layout settings
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL for system templates
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="templates")
    documents = relationship("Document", back_populates="template")


class Document(Base):
    """Generated documents with metadata and content"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    
    # Content
    original_transcription = Column(Text)
    content = Column(Text, nullable=False)
    formatted_content = Column(Text)  # HTML/Markdown formatted version
    
    # File information
    filename = Column(String(255))
    file_size = Column(Integer)
    file_format = Column(String(20))  # pdf, docx, md
    
    # Audio information
    audio_filename = Column(String(255))
    audio_duration = Column(Float)  # in seconds
    audio_quality_score = Column(Float)  # 0-1 quality assessment
    
    # Google Drive integration
    google_drive_file_id = Column(String(255))
    google_drive_url = Column(Text)
    
    # Processing metadata
    processing_time = Column(Float)  # in seconds
    ai_confidence_score = Column(Float)  # 0-1 AI confidence
    revision_count = Column(Integer, default=0)
    
    # User and template associations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="documents")
    template = relationship("Template", back_populates="documents")
    revisions = relationship("DocumentRevision", back_populates="document", cascade="all, delete-orphan")


class DocumentRevision(Base):
    """Document revision history"""
    __tablename__ = "document_revisions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    revision_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    change_summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="revisions")


class UsageStats(Base):
    """User usage statistics and analytics"""
    __tablename__ = "usage_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Usage metrics
    date = Column(DateTime(timezone=True), server_default=func.now())
    documents_created = Column(Integer, default=0)
    total_audio_minutes = Column(Float, default=0.0)
    total_processing_time = Column(Float, default=0.0)
    api_calls_made = Column(Integer, default=0)
    
    # Document type breakdown
    meeting_minutes_count = Column(Integer, default=0)
    letters_count = Column(Integer, default=0)
    reports_count = Column(Integer, default=0)
    announcements_count = Column(Integer, default=0)
    flyers_count = Column(Integer, default=0)
    custom_count = Column(Integer, default=0)
    
    # Quality metrics
    average_confidence_score = Column(Float)
    successful_generations = Column(Integer, default=0)
    failed_generations = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="usage_stats")


class SystemConfig(Base):
    """System configuration and feature flags"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AuditLog(Base):
    """Audit log for security and compliance"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")