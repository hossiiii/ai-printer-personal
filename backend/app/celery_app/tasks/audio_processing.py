"""
Audio processing tasks for enhanced voice-to-text pipeline
"""
from celery import current_task
from ..celery import celery_app
import librosa
import noisereduce as nr
import numpy as np
import webrtcvad
from pydub import AudioSegment
import io
import logging
from typing import Dict, Any
import tempfile
import os

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def enhance_audio_quality(self, audio_data: bytes, sample_rate: int = 16000) -> Dict[str, Any]:
    """
    Enhance audio quality using noise reduction and normalization
    
    Args:
        audio_data: Raw audio bytes
        sample_rate: Target sample rate for processing
        
    Returns:
        Dict containing enhanced audio data and quality metrics
    """
    try:
        # Update task progress
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Loading audio'})
        
        # Load audio data
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file.flush()
            
            # Load with librosa
            audio, sr = librosa.load(temp_file.name, sr=sample_rate)
            
        os.unlink(temp_file.name)
        
        self.update_state(state='PROGRESS', meta={'progress': 30, 'status': 'Analyzing audio quality'})
        
        # Calculate initial quality metrics
        initial_snr = calculate_snr(audio)
        initial_rms = np.sqrt(np.mean(audio**2))
        
        self.update_state(state='PROGRESS', meta={'progress': 50, 'status': 'Applying noise reduction'})
        
        # Apply noise reduction
        reduced_noise = nr.reduce_noise(y=audio, sr=sr, stationary=False, prop_decrease=0.8)
        
        self.update_state(state='PROGRESS', meta={'progress': 70, 'status': 'Normalizing audio'})
        
        # Normalize audio
        normalized_audio = librosa.util.normalize(reduced_noise)
        
        self.update_state(state='PROGRESS', meta={'progress': 90, 'status': 'Calculating final metrics'})
        
        # Calculate final quality metrics
        final_snr = calculate_snr(normalized_audio)
        final_rms = np.sqrt(np.mean(normalized_audio**2))
        
        # Convert back to bytes
        enhanced_audio_segment = AudioSegment(
            normalized_audio.tobytes(),
            frame_rate=sr,
            sample_width=2,
            channels=1
        )
        
        output_buffer = io.BytesIO()
        enhanced_audio_segment.export(output_buffer, format="wav")
        enhanced_audio_data = output_buffer.getvalue()
        
        return {
            'enhanced_audio': enhanced_audio_data,
            'quality_metrics': {
                'initial_snr': float(initial_snr),
                'final_snr': float(final_snr),
                'snr_improvement': float(final_snr - initial_snr),
                'initial_rms': float(initial_rms),
                'final_rms': float(final_rms),
                'duration': len(audio) / sr,
                'sample_rate': sr,
            },
            'processing_info': {
                'noise_reduction_applied': True,
                'normalization_applied': True,
                'quality_score': min(1.0, max(0.0, (final_snr + 10) / 30))  # Scale SNR to 0-1
            }
        }
        
    except Exception as exc:
        logger.error(f"Audio enhancement failed: {exc}")
        self.update_state(state='FAILURE', meta={'error': str(exc)})
        raise


@celery_app.task(bind=True)
def detect_speech_segments(self, audio_data: bytes, aggressiveness: int = 2) -> Dict[str, Any]:
    """
    Detect speech segments in audio using WebRTC VAD
    
    Args:
        audio_data: Raw audio bytes
        aggressiveness: VAD aggressiveness (0-3, higher = more aggressive)
        
    Returns:
        Dict containing speech segments and timing information
    """
    try:
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Loading audio for VAD'})
        
        # Load audio with pydub
        audio_segment = AudioSegment.from_wav(io.BytesIO(audio_data))
        
        # Ensure 16kHz mono for WebRTC VAD
        audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
        
        # Create VAD instance
        vad = webrtcvad.Vad(aggressiveness)
        
        self.update_state(state='PROGRESS', meta={'progress': 30, 'status': 'Analyzing speech segments'})
        
        # Process audio in 30ms frames
        frame_duration = 30  # ms
        frame_length = int(16000 * frame_duration / 1000)  # samples per frame
        
        speech_segments = []
        current_segment_start = None
        
        for i in range(0, len(audio_segment.raw_data), frame_length * 2):  # 2 bytes per sample
            frame = audio_segment.raw_data[i:i + frame_length * 2]
            
            if len(frame) < frame_length * 2:
                break
                
            # Check if frame contains speech
            is_speech = vad.is_speech(frame, 16000)
            timestamp = i / (16000 * 2)  # Convert to seconds
            
            if is_speech and current_segment_start is None:
                current_segment_start = timestamp
            elif not is_speech and current_segment_start is not None:
                speech_segments.append({
                    'start': current_segment_start,
                    'end': timestamp,
                    'duration': timestamp - current_segment_start
                })
                current_segment_start = None
        
        # Close final segment if needed
        if current_segment_start is not None:
            final_timestamp = len(audio_segment.raw_data) / (16000 * 2)
            speech_segments.append({
                'start': current_segment_start,
                'end': final_timestamp,
                'duration': final_timestamp - current_segment_start
            })
        
        self.update_state(state='PROGRESS', meta={'progress': 90, 'status': 'Calculating speech statistics'})
        
        # Calculate statistics
        total_duration = len(audio_segment) / 1000  # Convert to seconds
        speech_duration = sum(segment['duration'] for segment in speech_segments)
        speech_ratio = speech_duration / total_duration if total_duration > 0 else 0
        
        return {
            'speech_segments': speech_segments,
            'statistics': {
                'total_duration': total_duration,
                'speech_duration': speech_duration,
                'silence_duration': total_duration - speech_duration,
                'speech_ratio': speech_ratio,
                'num_segments': len(speech_segments),
                'aggressiveness_level': aggressiveness
            }
        }
        
    except Exception as exc:
        logger.error(f"Speech detection failed: {exc}")
        self.update_state(state='FAILURE', meta={'error': str(exc)})
        raise


@celery_app.task(bind=True)
def extract_audio_features(self, audio_data: bytes) -> Dict[str, Any]:
    """
    Extract comprehensive audio features for quality assessment
    
    Args:
        audio_data: Raw audio bytes
        
    Returns:
        Dict containing extracted audio features
    """
    try:
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Loading audio for feature extraction'})
        
        # Load audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file.flush()
            audio, sr = librosa.load(temp_file.name, sr=22050)
        
        os.unlink(temp_file.name)
        
        self.update_state(state='PROGRESS', meta={'progress': 30, 'status': 'Extracting spectral features'})
        
        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
        
        self.update_state(state='PROGRESS', meta={'progress': 60, 'status': 'Extracting MFCC features'})
        
        # MFCC features
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        
        self.update_state(state='PROGRESS', meta={'progress': 80, 'status': 'Calculating temporal features'})
        
        # Temporal features
        rms_energy = librosa.feature.rms(y=audio)[0]
        tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
        
        return {
            'spectral_features': {
                'centroid_mean': float(np.mean(spectral_centroids)),
                'centroid_std': float(np.std(spectral_centroids)),
                'rolloff_mean': float(np.mean(spectral_rolloff)),
                'rolloff_std': float(np.std(spectral_rolloff)),
                'bandwidth_mean': float(np.mean(spectral_bandwidth)),
                'bandwidth_std': float(np.std(spectral_bandwidth)),
                'zcr_mean': float(np.mean(zero_crossing_rate)),
                'zcr_std': float(np.std(zero_crossing_rate)),
            },
            'mfcc_features': {
                'mfcc_means': [float(x) for x in np.mean(mfccs, axis=1)],
                'mfcc_stds': [float(x) for x in np.std(mfccs, axis=1)],
            },
            'temporal_features': {
                'rms_mean': float(np.mean(rms_energy)),
                'rms_std': float(np.std(rms_energy)),
                'tempo': float(tempo),
                'duration': len(audio) / sr,
                'sample_rate': sr,
            },
            'quality_indicators': {
                'dynamic_range': float(np.max(audio) - np.min(audio)),
                'snr_estimate': float(calculate_snr(audio)),
                'silence_ratio': float(np.sum(np.abs(audio) < 0.01) / len(audio)),
            }
        }
        
    except Exception as exc:
        logger.error(f"Feature extraction failed: {exc}")
        self.update_state(state='FAILURE', meta={'error': str(exc)})
        raise


def calculate_snr(audio: np.ndarray) -> float:
    """Calculate Signal-to-Noise Ratio estimate"""
    # Simple SNR estimation using signal power vs noise floor
    signal_power = np.mean(audio**2)
    
    # Estimate noise as the lowest 10% of RMS values in frames
    frame_size = len(audio) // 100
    if frame_size < 1:
        return 0.0
        
    frame_rms = []
    for i in range(0, len(audio) - frame_size, frame_size):
        frame = audio[i:i + frame_size]
        frame_rms.append(np.sqrt(np.mean(frame**2)))
    
    if not frame_rms:
        return 0.0
        
    noise_estimate = np.percentile(frame_rms, 10)**2
    
    if noise_estimate == 0:
        return 50.0  # Very high SNR for perfect signal
        
    snr_linear = signal_power / noise_estimate
    snr_db = 10 * np.log10(snr_linear) if snr_linear > 0 else -50.0
    
    return max(-50.0, min(50.0, snr_db))  # Clamp to reasonable range