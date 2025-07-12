import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import './i18n';

import Header from './components/Header.tsx';
import VoiceRecorder from './components/VoiceRecorder.tsx';
import DocumentPreview from './components/DocumentPreview.tsx';
import FileHistory from './components/FileHistory.tsx';
import { DocumentResponse, TranscriptionResponse } from './types/index.ts';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2C3E50',
    },
    secondary: {
      main: '#3498DB',
    },
    background: {
      default: '#F8F9FA',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
});

const App: React.FC = () => {
  const [currentDocument, setCurrentDocument] = React.useState<DocumentResponse | undefined>();
  const [currentTranscription, setCurrentTranscription] = React.useState<TranscriptionResponse | undefined>();
  const [error, setError] = React.useState<string>('');

  const handleDocumentGenerated = (document: DocumentResponse, transcription: TranscriptionResponse) => {
    setCurrentDocument(document);
    setCurrentTranscription(transcription);
    setError('');
  };

  const handleDocumentUpdated = (document: DocumentResponse) => {
    setCurrentDocument(document);
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Header />
          <Container maxWidth="lg" sx={{ flex: 1, py: 4 }}>
            <Routes>
              <Route 
                path="/" 
                element={
                  <Box>
                    {error && (
                      <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
                        {error}
                      </Alert>
                    )}
                    <VoiceRecorder 
                      onDocumentGenerated={handleDocumentGenerated}
                      onError={handleError}
                    />
                    <Box sx={{ mt: 4 }}>
                      <DocumentPreview 
                        document={currentDocument}
                        transcription={currentTranscription}
                        onDocumentUpdated={handleDocumentUpdated}
                        onError={handleError}
                      />
                    </Box>
                  </Box>
                } 
              />
              <Route path="/history" element={<FileHistory />} />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App;
