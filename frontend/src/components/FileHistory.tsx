import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Divider,
  Card,
  CardContent,
  CardActions,
} from '@mui/material';
import {
  OpenInNew as OpenIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  PictureAsPdf as PdfIcon,
  Schedule as TimeIcon,
  Storage as SizeIcon,
} from '@mui/icons-material';

import { DriveAPI, handleAPIError } from '../services/api.ts';
import { FileHistoryItem } from '../types/index.ts';

const FileHistory: React.FC = () => {
  const [files, setFiles] = useState<FileHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [refreshing, setRefreshing] = useState(false);

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  // Format date
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return `Today at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    } else if (diffDays === 1) {
      return `Yesterday at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  // Extract document type from filename
  const getDocumentType = (filename: string): string => {
    const types = ['flyer', 'announcement', 'notice', 'event'];
    const lowerFilename = filename.toLowerCase();
    
    for (const type of types) {
      if (lowerFilename.includes(type)) {
        return type;
      }
    }
    return 'document';
  };

  // Load files from API
  const loadFiles = async (showRefreshIndicator = false) => {
    try {
      if (showRefreshIndicator) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      
      setError('');
      
      // For development mode, show mock data since Drive API requires authentication
      const isDevelopment = process.env.NODE_ENV === 'development';
      
      if (isDevelopment) {
        // Mock data for development
        const mockFiles: FileHistoryItem[] = [
          {
            file_id: 'mock_1',
            filename: 'event_summer_party_20240712_143022.pdf',
            drive_link: 'https://drive.google.com/file/d/mock_1/view',
            created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
            file_size: 245760, // 240 KB
          },
          {
            file_id: 'mock_2',
            filename: 'flyer_garage_sale_20240712_101530.pdf',
            drive_link: 'https://drive.google.com/file/d/mock_2/view',
            created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
            file_size: 189440, // 185 KB
          },
          {
            file_id: 'mock_3',
            filename: 'announcement_meeting_20240711_165045.pdf',
            drive_link: 'https://drive.google.com/file/d/mock_3/view',
            created_at: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(), // 2 days ago
            file_size: 167936, // 164 KB
          },
        ];
        
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        setFiles(mockFiles);
      } else {
        // Production mode - use actual API
        const filesData = await DriveAPI.getUserFiles(20);
        setFiles(filesData);
      }
      
    } catch (err) {
      console.error('Error loading files:', err);
      const errorResponse = handleAPIError(err);
      setError(errorResponse.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Open file in new tab
  const openFile = (file: FileHistoryItem) => {
    window.open(file.drive_link, '_blank');
  };

  // Download file (development mode only)
  const downloadFile = (file: FileHistoryItem) => {
    if (process.env.NODE_ENV === 'development') {
      // In development, create a download link to the API endpoint
      const link = document.createElement('a');
      link.href = `/api/download/${file.filename}`;
      link.download = file.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else {
      // In production, open the Drive link
      openFile(file);
    }
  };

  // Load files on component mount
  useEffect(() => {
    loadFiles();
  }, []);

  if (loading) {
    return (
      <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress size={40} />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Loading your documents...
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">
          Document History
        </Typography>
        
        <Button
          variant="outlined"
          startIcon={refreshing ? <CircularProgress size={16} /> : <RefreshIcon />}
          onClick={() => loadFiles(true)}
          disabled={refreshing}
        >
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {files.length === 0 && !error ? (
        <Alert severity="info">
          No documents found. Create your first document by recording audio!
        </Alert>
      ) : (
        <Box>
          {/* Summary */}
          <Box mb={3}>
            <Typography variant="body2" color="text.secondary">
              Found {files.length} document{files.length !== 1 ? 's' : ''} in your AI Printer collection
            </Typography>
          </Box>

          {/* File List */}
          <Box display="flex" flexDirection="column" gap={2}>
            {files.map((file, index) => (
              <Card key={file.file_id} variant="outlined">
                <CardContent sx={{ pb: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                    <Box flex={1}>
                      <Typography variant="h6" component="div" gutterBottom>
                        <PdfIcon sx={{ mr: 1, verticalAlign: 'middle', fontSize: 20 }} />
                        {file.filename.replace(/\.(pdf)$/i, '')}
                      </Typography>
                      
                      <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                        <Chip 
                          size="small"
                          label={getDocumentType(file.filename)}
                          color="primary"
                          variant="outlined"
                        />
                        <Chip 
                          size="small"
                          icon={<SizeIcon />}
                          label={formatFileSize(file.file_size)}
                          variant="outlined"
                        />
                        <Chip 
                          size="small"
                          icon={<TimeIcon />}
                          label={formatDate(file.created_at)}
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                  </Box>
                </CardContent>
                
                <CardActions sx={{ pt: 0 }}>
                  <Button
                    size="small"
                    startIcon={<OpenIcon />}
                    onClick={() => openFile(file)}
                  >
                    Open in Drive
                  </Button>
                  
                  {process.env.NODE_ENV === 'development' && (
                    <Button
                      size="small"
                      startIcon={<DownloadIcon />}
                      onClick={() => downloadFile(file)}
                    >
                      Download
                    </Button>
                  )}
                </CardActions>
              </Card>
            ))}
          </Box>

          {/* Footer Info */}
          {process.env.NODE_ENV === 'development' && (
            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="body2">
                <strong>Development Mode:</strong> Showing mock data. 
                In production, this will show your actual Google Drive files.
              </Typography>
            </Alert>
          )}
        </Box>
      )}
    </Paper>
  );
};

export default FileHistory;