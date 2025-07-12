import axios from 'axios';
import {
  TranscriptionResponse,
  DocumentResponse,
  PDFGenerationResponse,
  FileHistoryItem,
  ErrorResponse
} from '../types/index.ts';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to auth
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

export class AudioAPI {
  static async transcribeAudio(
    audioBlob: Blob,
    language?: string
  ): Promise<TranscriptionResponse> {
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.webm');
    
    if (language) {
      formData.append('language', language);
    }

    const response = await api.post('/api/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }
}

export class DocumentAPI {
  static async generateDocument(
    transcription: string,
    documentType?: string,
    customInstructions?: string
  ): Promise<DocumentResponse> {
    const response = await api.post('/api/generate-document', {
      transcription,
      document_type: documentType,
      custom_instructions: customInstructions,
    });

    return response.data;
  }

  static async generatePDF(
    htmlContent: string,
    cssContent: string,
    documentTitle: string,
    documentType: string,
    saveToDrive: boolean = true
  ): Promise<PDFGenerationResponse> {
    const response = await api.post('/api/generate-pdf', {
      html_content: htmlContent,
      css_content: cssContent,
      document_title: documentTitle,
      document_type: documentType,
      save_to_drive: saveToDrive,
    });

    return response.data;
  }

  static async reviseDocument(
    originalContent: Record<string, any>,
    revisionInstruction: string,
    revisionType: 'voice' | 'text' = 'text'
  ): Promise<DocumentResponse> {
    const response = await api.post('/api/revise-document', {
      original_content: originalContent,
      revision_instruction: revisionInstruction,
      revision_type: revisionType,
    });

    return response.data;
  }
}

export class DriveAPI {
  static async getAuthUrl(): Promise<{ auth_url: string }> {
    const response = await api.get('/api/drive/auth-url');
    return response.data;
  }

  static async exchangeCode(code: string): Promise<{ 
    access_token: string;
    refresh_token: string;
  }> {
    const response = await api.post('/api/drive/exchange-code', { code });
    return response.data;
  }

  static async getUserFiles(limit: number = 10): Promise<FileHistoryItem[]> {
    const response = await api.get(`/api/drive/files?limit=${limit}`);
    return response.data.files || [];
  }
}

export class HealthAPI {
  static async checkHealth(): Promise<{ status: string; timestamp: string }> {
    const response = await api.get('/health');
    return response.data;
  }
}

// Utility function to handle API errors
export const handleAPIError = (error: any): ErrorResponse => {
  if (error.response?.data) {
    return error.response.data;
  }
  
  return {
    error: 'NetworkError',
    message: error.message || 'Network error occurred',
    timestamp: new Date().toISOString(),
  };
};

export default api;
