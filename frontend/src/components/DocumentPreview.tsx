import React, { useState, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  PictureAsPdf as PdfIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Fullscreen as FullscreenIcon,
} from '@mui/icons-material';

import { DocumentAPI, handleAPIError } from '../services/api.ts';
import { DocumentResponse, TranscriptionResponse, PDFGenerationResponse } from '../types/index.ts';

interface DocumentPreviewProps {
  document?: DocumentResponse;
  transcription?: TranscriptionResponse;
  onDocumentUpdated?: (document: DocumentResponse) => void;
  onError?: (error: string) => void;
}

const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  document,
  transcription,
  onDocumentUpdated,
  onError,
}) => {
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [isRevising, setIsRevising] = useState(false);
  const [revisionText, setRevisionText] = useState('');
  const [pdfResult, setPdfResult] = useState<PDFGenerationResponse | null>(null);
  const [fullscreenOpen, setFullscreenOpen] = useState(false);
  
  const previewRef = useRef<HTMLDivElement>(null);

  // Generate PDF from current document
  const generatePDF = async () => {
    if (!document) {
      onError?.('No document to convert to PDF');
      return;
    }

    try {
      setIsGeneratingPDF(true);
      
      const result = await DocumentAPI.generatePDF(
        document.html_content,
        document.css_content,
        document.title,
        document.document_type
      );
      
      setPdfResult(result);
      setIsGeneratingPDF(false);
      
    } catch (error) {
      console.error('Error generating PDF:', error);
      const errorResponse = handleAPIError(error);
      onError?.(errorResponse.message);
      setIsGeneratingPDF(false);
    }
  };

  // Revise document based on text input
  const reviseDocument = async () => {
    if (!document || !revisionText.trim()) {
      onError?.('Please enter revision instructions');
      return;
    }

    try {
      setIsRevising(true);
      
      const revisedDocument = await DocumentAPI.reviseDocument(
        {
          html_content: document.html_content,
          css_content: document.css_content,
          title: document.title,
          document_type: document.document_type,
        },
        revisionText,
        'text'
      );
      
      onDocumentUpdated?.(revisedDocument);
      setRevisionText('');
      setIsRevising(false);
      
    } catch (error) {
      console.error('Error revising document:', error);
      const errorResponse = handleAPIError(error);
      onError?.(errorResponse.message);
      setIsRevising(false);
    }
  };

  // Download PDF (development mode)
  const downloadPDF = () => {
    if (pdfResult?.file_path) {
      const link = document.createElement('a');
      link.href = `/api/download/${pdfResult.filename}`;
      link.download = pdfResult.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  // Share Drive link
  const shareDriveLink = () => {
    if (pdfResult?.drive_link) {
      navigator.clipboard.writeText(pdfResult.drive_link);
      // Could show a snackbar here
      alert('Drive link copied to clipboard!');
    }
  };

  // Open fullscreen preview
  const openFullscreen = () => {
    setFullscreenOpen(true);
  };

  if (!document) {
    return (
      <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Record audio to generate document preview
        </Typography>
      </Paper>
    );
  }

  return (
    <>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h5">
            Document Preview
          </Typography>
          
          <Box display="flex" gap={1}>
            <Tooltip title="View Fullscreen">
              <IconButton onClick={openFullscreen}>
                <FullscreenIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Document Info */}
        <Box display="flex" gap={1} mb={2} flexWrap="wrap">
          <Chip 
            label={`Type: ${document.document_type}`}
            variant="outlined"
            color="primary"
          />
          <Chip 
            label={`Title: ${document.title}`}
            variant="outlined"
          />
          {transcription && (
            <Chip 
              label={`Confidence: ${Math.round(transcription.confidence * 100)}%`}
              variant="outlined"
              color={transcription.confidence > 0.8 ? 'success' : 'warning'}
            />
          )}
        </Box>

        {/* Document Preview */}
        <Paper 
          ref={previewRef}
          variant="outlined" 
          sx={{ 
            p: 2, 
            mb: 3, 
            minHeight: 300,
            maxHeight: 500,
            overflow: 'auto',
            backgroundColor: '#fafafa',
          }}
        >
          <div
            dangerouslySetInnerHTML={{
              __html: `
                <style>${document.css_content}</style>
                ${document.html_content}
              `
            }}
          />
        </Paper>

        {/* Revision Section */}
        <Box mb={3}>
          <Typography variant="h6" gutterBottom>
            Revise Document
          </Typography>
          
          <Box display="flex" gap={2} alignItems="flex-start">
            <TextField
              fullWidth
              multiline
              rows={2}
              placeholder="Enter revision instructions (e.g., 'make the title bigger', 'change the date to tomorrow', 'add contact information')"
              value={revisionText}
              onChange={(e) => setRevisionText(e.target.value)}
              disabled={isRevising}
            />
            
            <Button
              variant="outlined"
              startIcon={isRevising ? <CircularProgress size={16} /> : <EditIcon />}
              onClick={reviseDocument}
              disabled={isRevising || !revisionText.trim()}
              sx={{ minWidth: 120 }}
            >
              {isRevising ? 'Revising...' : 'Revise'}
            </Button>
          </Box>
        </Box>

        {/* PDF Generation */}
        <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
          <Button
            variant="contained"
            size="large"
            startIcon={isGeneratingPDF ? <CircularProgress size={16} /> : <PdfIcon />}
            onClick={generatePDF}
            disabled={isGeneratingPDF}
            color="secondary"
          >
            {isGeneratingPDF ? 'Generating PDF...' : 'Generate PDF'}
          </Button>

          {pdfResult && (
            <>
              {pdfResult.file_path && (
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={downloadPDF}
                >
                  Download PDF
                </Button>
              )}
              
              {pdfResult.drive_link && (
                <Button
                  variant="outlined"
                  startIcon={<ShareIcon />}
                  onClick={shareDriveLink}
                >
                  Share Drive Link
                </Button>
              )}
            </>
          )}
        </Box>

        {/* PDF Generation Success */}
        {pdfResult && (
          <Alert severity="success" sx={{ mt: 2 }}>
            <Typography variant="body2">
              PDF generated successfully! 
              {pdfResult.file_size && ` Size: ${(pdfResult.file_size / 1024).toFixed(1)} KB`}
              {pdfResult.drive_link && ` | Saved to Google Drive`}
            </Typography>
          </Alert>
        )}
      </Paper>

      {/* Fullscreen Preview Dialog */}
      <Dialog
        open={fullscreenOpen}
        onClose={() => setFullscreenOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: { height: '90vh' }
        }}
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              {document.title} - Full Preview
            </Typography>
            <Chip label={document.document_type} color="primary" />
          </Box>
        </DialogTitle>
        
        <DialogContent sx={{ p: 3 }}>
          <Paper 
            variant="outlined" 
            sx={{ 
              p: 3, 
              height: '100%',
              overflow: 'auto',
              backgroundColor: 'white',
            }}
          >
            <div
              dangerouslySetInnerHTML={{
                __html: `
                  <style>${document.css_content}</style>
                  ${document.html_content}
                `
              }}
            />
          </Paper>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setFullscreenOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default DocumentPreview;