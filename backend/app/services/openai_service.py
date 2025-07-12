"""
OpenAI Service Integration
Handles Whisper API for transcription and GPT API for document generation
"""
import asyncio
import tempfile
import time
import logging
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from ..config import settings
from ..models.audio import TranscriptionResponse, DocumentResponse

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI API integration"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY and not settings.DEVELOPMENT:
            raise ValueError("OPENAI_API_KEY not configured")
        
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY or "mock-key-for-development")
        self.whisper_model = settings.WHISPER_MODEL
        self.gpt_model = settings.OPENAI_MODEL
    
    async def transcribe_audio(
        self, 
        audio_data: bytes, 
        language: Optional[str] = None
    ) -> TranscriptionResponse:
        """
        Transcribe audio using OpenAI Whisper API
        
        Args:
            audio_data: Audio file data in bytes
            language: Language code (optional, auto-detect if None)
            
        Returns:
            TranscriptionResponse with transcribed text and metadata
        """
        start_time = time.time()
        
        # Validate file size
        if len(audio_data) > settings.MAX_AUDIO_FILE_SIZE:
            raise ValueError(f"Audio file too large: {len(audio_data)} bytes")
        
        logger.info(f"Starting transcription for {len(audio_data)} bytes audio")
        
        try:
            # Create temporary file for OpenAI API
            import os
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Transcribe using Whisper API
            with open(temp_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=self.whisper_model,
                    file=audio_file,
                    language=language
                )
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            processing_time = time.time() - start_time
            
            logger.info(f"Transcription completed in {processing_time:.2f}s")
            
            return TranscriptionResponse(
                text=response.text,
                language=getattr(response, 'language', 'unknown'),
                confidence=1.0,  # Whisper doesn't provide confidence scores
                duration=getattr(response, 'duration', 0.0),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise Exception(f"Audio transcription failed: {str(e)}")
    
    async def generate_document(
        self,
        transcription: str,
        document_type: Optional[str] = None,
        custom_instructions: Optional[str] = None
    ) -> DocumentResponse:
        """
        Generate document content using GPT API
        
        Args:
            transcription: Transcribed text from audio
            document_type: Type of document to generate
            custom_instructions: Additional instructions
            
        Returns:
            DocumentResponse with HTML/CSS content
        """
        logger.info(f"Generating document from transcription: {transcription[:100]}...")
        
        try:
            # Determine document type if not provided
            if not document_type:
                document_type = await self._analyze_document_type(transcription)
            
            # Generate document content
            system_prompt = self._build_system_prompt(document_type)
            user_prompt = self._build_user_prompt(transcription, custom_instructions)
            
            response = await self.client.chat.completions.create(
                model=self.gpt_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = self._parse_document_response(response.choices[0].message.content)
            
            logger.info(f"Document generated successfully for type: {document_type}")
            
            return DocumentResponse(
                html_content=content["html"],
                css_content=content["css"],
                document_type=document_type,
                title=content["title"],
                metadata={
                    "generated_at": time.time(),
                    "source_transcription": transcription,
                    "custom_instructions": custom_instructions
                }
            )
            
        except Exception as e:
            logger.error(f"Document generation failed: {e}")
            raise Exception(f"Document generation failed: {str(e)}")
    
    async def _analyze_document_type(self, transcription: str) -> str:
        """Analyze transcription to determine document type"""
        
        analysis_prompt = f"""
        Analyze this transcription and determine what type of document should be created.
        Choose from: flyer, announcement, notice, event
        
        Transcription: "{transcription}"
        
        Respond with only the document type.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.gpt_model,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.1,
                max_tokens=10
            )
            
            doc_type = response.choices[0].message.content.strip().lower()
            
            if doc_type not in settings.SUPPORTED_DOCUMENT_TYPES:
                return "flyer"  # Default fallback
                
            return doc_type
            
        except Exception as e:
            logger.warning(f"Document type analysis failed: {e}, using default")
            return "flyer"
    
    def _build_system_prompt(self, document_type: str) -> str:
        """Build system prompt for document generation"""
        
        base_prompt = """
        You are a professional document designer creating high-quality printed materials.
        Generate content that is visually appealing, clear, and effective.
        """
        
        type_specific = {
            "flyer": "Create an eye-catching flyer with clear hierarchy and compelling call-to-action.",
            "announcement": "Create a formal announcement with important information prominently displayed.",
            "notice": "Create a clear notice with essential information that's easy to read quickly.",
            "event": "Create an engaging event invitation with all necessary details."
        }
        
        return f"{base_prompt}\n\n{type_specific.get(document_type, type_specific['flyer'])}"
    
    def _build_user_prompt(self, transcription: str, custom_instructions: Optional[str]) -> str:
        """Build user prompt for document generation"""
        
        prompt = f"""
        Create a professional document based on this voice instruction:
        "{transcription}"
        
        {f"Additional instructions: {custom_instructions}" if custom_instructions else ""}
        
        Provide your response in this exact JSON format:
        {{
            "title": "Document title",
            "html": "<div class='document'>HTML content here</div>",
            "css": ".document {{ CSS styles here }}"
        }}
        
        Requirements:
        - Professional, modern design
        - Clear hierarchy and readability
        - Responsive layout
        - Include all relevant information from the transcription
        - Use appropriate fonts, colors, and spacing
        """
        
        return prompt
    
    def _parse_document_response(self, response_content: str) -> Dict[str, str]:
        """Parse GPT response to extract document components"""
        
        try:
            import json
            
            # Try to parse as JSON first
            if response_content.strip().startswith('{'):
                content = json.loads(response_content)
                return {
                    "title": content.get("title", "Generated Document"),
                    "html": content.get("html", "<div>Content not generated</div>"),
                    "css": content.get("css", ".document { font-family: Arial, sans-serif; }")
                }
            
            # Fallback: Extract components manually
            return self._extract_components_manually(response_content)
            
        except Exception as e:
            logger.warning(f"Failed to parse document response: {e}")
            return {
                "title": "Generated Document",
                "html": f"<div class='document'><h1>Generated Content</h1><p>{response_content}</p></div>",
                "css": ".document { font-family: Arial, sans-serif; padding: 20px; }"
            }
    
    def _extract_components_manually(self, content: str) -> Dict[str, str]:
        """Manually extract HTML/CSS components from response"""
        
        # Simple extraction logic - can be enhanced
        html_start = content.find("<")
        css_start = content.find("{")
        
        if html_start != -1 and css_start != -1:
            html_part = content[html_start:css_start].strip()
            css_part = content[css_start:].strip()
        else:
            html_part = f"<div class='document'>{content}</div>"
            css_part = ".document { font-family: Arial, sans-serif; padding: 20px; }"
        
        return {
            "title": "Generated Document",
            "html": html_part,
            "css": css_part
        }

# Global service instance
openai_service = OpenAIService()

def get_openai_service() -> OpenAIService:
    """Get OpenAI service instance"""
    return openai_service
