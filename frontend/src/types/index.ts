// API Response Types
export interface TranscriptionResponse {
  text: string;
  language: string;
  confidence: number;
  duration: number;
  processing_time: number;
}

export interface DocumentResponse {
  html_content: string;
  css_content: string;
  document_type: string;
  title: string;
  metadata: Record<string, any>;
}

export interface PDFGenerationResponse {
  success: boolean;
  file_path?: string;
  drive_link?: string;
  filename: string;
  file_size: number;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

// UI State Types
export interface RecordingState {
  isRecording: boolean;
  duration: number;
  audioBlob?: Blob;
  audioUrl?: string;
}

export interface ProcessingState {
  isTranscribing: boolean;
  isGeneratingDocument: boolean;
  isGeneratingPDF: boolean;
  error?: string;
}

export interface DocumentState {
  transcription?: TranscriptionResponse;
  document?: DocumentResponse;
  pdf?: PDFGenerationResponse;
  previewHtml?: string;
}

// Document Types
export type DocumentType = 'flyer' | 'announcement' | 'notice' | 'event';

// File History Types
export interface FileHistoryItem {
  file_id: string;
  filename: string;
  drive_link: string;
  created_at: string;
  file_size: number;
}
