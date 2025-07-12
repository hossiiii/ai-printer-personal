import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  IconButton,
  LinearProgress,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Mic as MicIcon,
  Stop as StopIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

import { AudioAPI, DocumentAPI, handleAPIError } from '../services/api.ts';
import { RecordingState, ProcessingState, DocumentResponse, TranscriptionResponse } from '../types/index.ts';

interface VoiceRecorderProps {
  onDocumentGenerated?: (document: DocumentResponse, transcription: TranscriptionResponse) => void;
  onError?: (error: string) => void;
}

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onDocumentGenerated,
  onError,
}) => {
  const [recordingState, setRecordingState] = useState<RecordingState>({
    isRecording: false,
    duration: 0,
  });
  
  const [processingState, setProcessingState] = useState<ProcessingState>({
    isTranscribing: false,
    isGeneratingDocument: false,
    isGeneratingPDF: false,
  });
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [transcriptionText, setTranscriptionText] = useState<string>('');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Format duration helper
  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Start recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: { 
          sampleRate: 44100,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        } 
      });
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        stream.getTracks().forEach(track => track.stop());
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        setRecordingState(prev => ({
          ...prev,
          audioBlob,
          audioUrl,
          isRecording: false,
        }));
      };
      
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(1000); // Collect data every second
      
      setRecordingState(prev => ({ ...prev, isRecording: true, duration: 0 }));
      setTranscriptionText('');
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingState(prev => ({ ...prev, duration: prev.duration + 1 }));
      }, 1000);
      
    } catch (error) {
      console.error('Error starting recording:', error);
      onError?.('Failed to start recording. Please check microphone permissions.');
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && recordingState.isRecording) {
      mediaRecorderRef.current.stop();
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  // Play/pause audio
  const togglePlayback = () => {
    if (!audioPlayerRef.current || !recordingState.audioUrl) return;
    
    if (isPlaying) {
      audioPlayerRef.current.pause();
      setIsPlaying(false);
    } else {
      audioPlayerRef.current.play();
      setIsPlaying(true);
    }
  };

  // Delete recording
  const deleteRecording = () => {
    if (recordingState.audioUrl) {
      URL.revokeObjectURL(recordingState.audioUrl);
    }
    
    setRecordingState({
      isRecording: false,
      duration: 0,
    });
    setTranscriptionText('');
    setIsPlaying(false);
  };

  // Process audio (transcribe and generate document)
  const processAudio = async () => {
    if (!recordingState.audioBlob) {
      onError?.('No audio recording available');
      return;
    }

    try {
      // Step 1: Transcribe audio
      setProcessingState(prev => ({ ...prev, isTranscribing: true }));
      
      const transcription = await AudioAPI.transcribeAudio(recordingState.audioBlob);
      setTranscriptionText(transcription.text);
      
      setProcessingState(prev => ({ ...prev, isTranscribing: false, isGeneratingDocument: true }));
      
      // Step 2: Generate document
      const document = await DocumentAPI.generateDocument(transcription.text);
      
      setProcessingState(prev => ({ ...prev, isGeneratingDocument: false }));
      
      // Notify parent component
      onDocumentGenerated?.(document, transcription);
      
    } catch (error) {
      console.error('Error processing audio:', error);
      const errorResponse = handleAPIError(error);
      onError?.(errorResponse.message);
      
      setProcessingState({
        isTranscribing: false,
        isGeneratingDocument: false,
        isGeneratingPDF: false,
      });
    }
  };

  // Setup audio player event listeners
  useEffect(() => {
    if (recordingState.audioUrl) {
      const audio = new Audio(recordingState.audioUrl);
      audio.onended = () => setIsPlaying(false);
      audioPlayerRef.current = audio;
      
      return () => {
        audio.pause();
        audio.src = '';
      };
    }
  }, [recordingState.audioUrl]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (recordingState.audioUrl) {
        URL.revokeObjectURL(recordingState.audioUrl);
      }
    };
  }, []);

  const isProcessing = processingState.isTranscribing || processingState.isGeneratingDocument;
  const hasRecording = !!recordingState.audioBlob && !recordingState.isRecording;

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h5" gutterBottom>
        Voice Recording
      </Typography>
      
      <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
        {/* Recording Status */}
        {recordingState.isRecording && (
          <Box textAlign="center">
            <Typography variant="h6" color="error">
              Recording...
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {formatDuration(recordingState.duration)}
            </Typography>
            <LinearProgress 
              sx={{ mt: 1, width: 200 }} 
              color="error"
            />
          </Box>
        )}
        
        {/* Main Controls */}
        <Box display="flex" gap={2} alignItems="center">
          {!recordingState.isRecording ? (
            <Button
              variant="contained"
              size="large"
              startIcon={<MicIcon />}
              onClick={startRecording}
              disabled={isProcessing}
              color="primary"
              sx={{ minWidth: 140 }}
            >
              Start Recording
            </Button>
          ) : (
            <Button
              variant="contained"
              size="large"
              startIcon={<StopIcon />}
              onClick={stopRecording}
              color="error"
              sx={{ minWidth: 140 }}
            >
              Stop Recording
            </Button>
          )}
        </Box>
        
        {/* Recording Playback Controls */}
        {hasRecording && (
          <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
            <Chip 
              label={`Recording: ${formatDuration(recordingState.duration)}`}
              variant="outlined"
              color="primary"
            />
            
            <Box display="flex" gap={1}>
              <IconButton 
                onClick={togglePlayback}
                color="primary"
                size="large"
              >
                {isPlaying ? <PauseIcon /> : <PlayIcon />}
              </IconButton>
              
              <IconButton 
                onClick={deleteRecording}
                color="error"
                size="large"
              >
                <DeleteIcon />
              </IconButton>
            </Box>
          </Box>
        )}
        
        {/* Processing Status */}
        {isProcessing && (
          <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
            <CircularProgress size={40} />
            <Typography variant="body2">
              {processingState.isTranscribing && 'Transcribing audio...'}
              {processingState.isGeneratingDocument && 'Generating document...'}
            </Typography>
          </Box>
        )}
        
        {/* Transcription Display */}
        {transcriptionText && (
          <Alert severity="info" sx={{ width: '100%', mt: 2 }}>
            <Typography variant="body2">
              <strong>Transcription:</strong> {transcriptionText}
            </Typography>
          </Alert>
        )}
        
        {/* Process Button */}
        {hasRecording && !isProcessing && (
          <Button
            variant="contained"
            size="large"
            onClick={processAudio}
            color="secondary"
            sx={{ mt: 2 }}
          >
            Generate Document
          </Button>
        )}
      </Box>
    </Paper>
  );
};

export default VoiceRecorder;