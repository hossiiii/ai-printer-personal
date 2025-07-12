"""
Enhanced audio processing service with noise reduction and quality analysis
"""
import asyncio
from typing import Dict, Any, Optional, Tuple
import tempfile
import os
import logging
from io import BytesIO
import numpy as np
from ..celery_app.tasks.audio_processing import (
    enhance_audio_quality,
    detect_speech_segments, 
    extract_audio_features
)
from ..celery_app.celery import celery_app
from .openai_service import OpenAIService
from ..config import settings

logger = logging.getLogger(__name__)


class EnhancedAudioService:
    """Enhanced audio processing with AI-powered quality improvements"""
    
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        self.temp_dir = settings.UPLOAD_DIR
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def process_audio_with_enhancement(
        self,
        audio_data: bytes,
        filename: str,
        enable_enhancement: bool = True,
        enhancement_level: str = "balanced"  # minimal, balanced, aggressive
    ) -> Dict[str, Any]:
        """
        Process audio with optional enhancement and quality analysis
        
        Args:
            audio_data: Raw audio bytes
            filename: Original filename
            enable_enhancement: Whether to apply audio enhancement
            enhancement_level: Level of enhancement to apply
            
        Returns:
            Complete processing results including transcription and quality metrics
        """
        try:
            # Start multiple tasks in parallel
            tasks = {}
            
            if enable_enhancement:
                # Start audio enhancement task
                enhancement_task = enhance_audio_quality.delay(
                    audio_data, 
                    sample_rate=16000 if enhancement_level != "minimal" else 8000
                )
                tasks['enhancement'] = enhancement_task
            
            # Start feature extraction for quality analysis
            feature_task = extract_audio_features.delay(audio_data)
            tasks['features'] = feature_task
            
            # Start speech detection
            aggressiveness = {"minimal": 1, "balanced": 2, "aggressive": 3}[enhancement_level]
            vad_task = detect_speech_segments.delay(audio_data, aggressiveness)
            tasks['vad'] = vad_task
            
            # Wait for tasks to complete
            results = {}
            
            # Get enhancement results if enabled
            if enable_enhancement:
                logger.info("Waiting for audio enhancement...")
                enhancement_result = enhancement_task.get(timeout=300)
                results['enhancement'] = enhancement_result
                
                # Use enhanced audio for transcription
                transcription_audio = enhancement_result['enhanced_audio']
                quality_score = enhancement_result['processing_info']['quality_score']
            else:
                transcription_audio = audio_data
                quality_score = 0.5  # Default for unprocessed audio
            
            # Get feature extraction results
            logger.info("Waiting for feature extraction...")
            feature_result = feature_task.get(timeout=120)
            results['features'] = feature_result
            
            # Get VAD results
            logger.info("Waiting for speech detection...")
            vad_result = vad_task.get(timeout=120)
            results['vad'] = vad_result
            
            # Perform transcription
            logger.info("Starting transcription with enhanced audio...")
            transcription_result = await self._transcribe_audio(
                transcription_audio, 
                filename,
                quality_score
            )
            results['transcription'] = transcription_result
            
            # Calculate comprehensive quality assessment
            quality_assessment = self._calculate_quality_assessment(
                results['features'],
                results['vad'],
                results.get('enhancement'),
                transcription_result
            )
            
            return {
                'transcription': transcription_result,
                'quality_assessment': quality_assessment,
                'processing_details': {
                    'enhancement_applied': enable_enhancement,
                    'enhancement_level': enhancement_level,
                    'speech_segments': results['vad']['speech_segments'],
                    'audio_features': results['features'],
                    'enhancement_metrics': results.get('enhancement', {}).get('quality_metrics', {}),
                },
                'recommendations': self._generate_recommendations(quality_assessment, results)
            }
            
        except Exception as e:
            logger.error(f"Enhanced audio processing failed: {e}")
            # Fallback to basic transcription
            try:
                basic_transcription = await self._transcribe_audio(audio_data, filename, 0.3)
                return {
                    'transcription': basic_transcription,
                    'quality_assessment': {'overall_score': 0.3, 'issues': ['processing_failed']},
                    'processing_details': {'enhancement_applied': False, 'fallback_used': True},
                    'error': str(e)
                }
            except Exception as fallback_error:
                logger.error(f"Fallback transcription also failed: {fallback_error}")
                raise
    
    async def _transcribe_audio(
        self, 
        audio_data: bytes, 
        filename: str,
        quality_score: float
    ) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper with quality-aware settings"""
        
        # Adjust transcription parameters based on quality
        if quality_score > 0.8:
            # High quality audio - use standard settings
            temperature = 0.0
            response_format = "verbose_json"
        elif quality_score > 0.5:
            # Medium quality - slightly more flexible
            temperature = 0.2
            response_format = "verbose_json"
        else:
            # Lower quality - more flexible, focus on word-level confidence
            temperature = 0.4
            response_format = "verbose_json"
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file.flush()
            
            try:
                # Call OpenAI Whisper
                result = await self.openai_service.transcribe_audio(
                    temp_file.name,
                    response_format=response_format,
                    temperature=temperature,
                    language=None  # Auto-detect
                )
                
                # Extract word-level confidence if available
                word_confidences = []
                if hasattr(result, 'segments'):
                    for segment in result.segments:
                        if hasattr(segment, 'words'):
                            for word in segment.words:
                                if hasattr(word, 'confidence'):
                                    word_confidences.append(word.confidence)
                
                avg_confidence = np.mean(word_confidences) if word_confidences else 0.8
                
                return {
                    'text': result.text,
                    'language': getattr(result, 'language', 'en'),
                    'duration': getattr(result, 'duration', 0),
                    'segments': getattr(result, 'segments', []),
                    'confidence_score': float(avg_confidence),
                    'processing_quality': quality_score,
                    'model_used': settings.WHISPER_MODEL,
                    'temperature_used': temperature
                }
                
            finally:
                os.unlink(temp_file.name)
    
    def _calculate_quality_assessment(
        self,
        features: Dict[str, Any],
        vad_result: Dict[str, Any],
        enhancement_result: Optional[Dict[str, Any]],
        transcription_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate comprehensive audio quality assessment"""
        
        scores = {}
        issues = []
        
        # Analyze audio features
        spectral_features = features['spectral_features']
        temporal_features = features['temporal_features']
        quality_indicators = features['quality_indicators']
        
        # SNR Assessment
        snr = quality_indicators['snr_estimate']
        if snr > 20:
            scores['snr'] = 1.0
        elif snr > 10:
            scores['snr'] = 0.7
        elif snr > 0:
            scores['snr'] = 0.5
        else:
            scores['snr'] = 0.2
            issues.append('low_snr')
        
        # Speech-to-silence ratio
        speech_ratio = vad_result['statistics']['speech_ratio']
        if speech_ratio > 0.7:
            scores['speech_content'] = 1.0
        elif speech_ratio > 0.4:
            scores['speech_content'] = 0.8
        elif speech_ratio > 0.2:
            scores['speech_content'] = 0.6
        else:
            scores['speech_content'] = 0.3
            issues.append('insufficient_speech')
        
        # Dynamic range assessment
        dynamic_range = quality_indicators['dynamic_range']
        if dynamic_range > 0.5:
            scores['dynamic_range'] = 1.0
        elif dynamic_range > 0.2:
            scores['dynamic_range'] = 0.7
        else:
            scores['dynamic_range'] = 0.4
            issues.append('low_dynamic_range')
        
        # Transcription confidence
        transcription_confidence = transcription_result.get('confidence_score', 0.5)
        scores['transcription_confidence'] = transcription_confidence
        
        if transcription_confidence < 0.6:
            issues.append('low_transcription_confidence')
        
        # Enhancement effectiveness (if applied)
        if enhancement_result:
            snr_improvement = enhancement_result['quality_metrics']['snr_improvement']
            if snr_improvement > 5:
                scores['enhancement_effectiveness'] = 1.0
            elif snr_improvement > 2:
                scores['enhancement_effectiveness'] = 0.8
            else:
                scores['enhancement_effectiveness'] = 0.5
        
        # Overall score calculation
        weight_map = {
            'snr': 0.3,
            'speech_content': 0.25,
            'dynamic_range': 0.15,
            'transcription_confidence': 0.2,
            'enhancement_effectiveness': 0.1
        }
        
        overall_score = sum(
            scores.get(key, 0.5) * weight 
            for key, weight in weight_map.items()
        )
        
        # Quality grade
        if overall_score >= 0.8:
            grade = 'excellent'
        elif overall_score >= 0.6:
            grade = 'good'
        elif overall_score >= 0.4:
            grade = 'fair'
        else:
            grade = 'poor'
        
        return {
            'overall_score': round(overall_score, 2),
            'grade': grade,
            'component_scores': scores,
            'issues': issues,
            'metrics': {
                'snr_db': snr,
                'speech_ratio': speech_ratio,
                'dynamic_range': dynamic_range,
                'transcription_confidence': transcription_confidence,
                'enhancement_improvement': enhancement_result['quality_metrics']['snr_improvement'] if enhancement_result else 0
            }
        }
    
    def _generate_recommendations(
        self,
        quality_assessment: Dict[str, Any],
        processing_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate actionable recommendations for improving audio quality"""
        
        recommendations = []
        technical_suggestions = []
        
        issues = quality_assessment['issues']
        overall_score = quality_assessment['overall_score']
        
        if 'low_snr' in issues:
            recommendations.append({
                'type': 'recording_environment',
                'title': 'Reduce Background Noise',
                'description': 'Record in a quieter environment or use noise-canceling equipment',
                'priority': 'high'
            })
            technical_suggestions.append('Use aggressive noise reduction')
        
        if 'insufficient_speech' in issues:
            recommendations.append({
                'type': 'recording_technique',
                'title': 'Increase Speech Content',
                'description': 'Speak more clearly and reduce silent pauses',
                'priority': 'medium'
            })
        
        if 'low_dynamic_range' in issues:
            recommendations.append({
                'type': 'recording_equipment',
                'title': 'Improve Recording Equipment',
                'description': 'Use a better microphone or adjust recording levels',
                'priority': 'medium'
            })
        
        if 'low_transcription_confidence' in issues:
            recommendations.append({
                'type': 'speech_clarity',
                'title': 'Improve Speech Clarity',
                'description': 'Speak more slowly and articulate words clearly',
                'priority': 'high'
            })
        
        # Enhancement recommendations
        enhancement_applied = processing_results.get('enhancement_applied', False)
        if not enhancement_applied and overall_score < 0.6:
            technical_suggestions.append('Enable audio enhancement for better results')
        
        return {
            'user_recommendations': recommendations,
            'technical_suggestions': technical_suggestions,
            'next_steps': [
                'Review transcription accuracy',
                'Apply recommended improvements for future recordings',
                'Consider re-recording if quality is insufficient'
            ]
        }