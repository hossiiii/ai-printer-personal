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
            logger.error(f"音声文字起こしが失敗しました: {e}")
            raise Exception(f"音声の文字起こしに失敗しました: {str(e)}")
    
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
            logger.error(f"文書生成が失敗しました: {e}")
            raise Exception(f"文書の生成に失敗しました: {str(e)}")
    
    async def _analyze_document_type(self, transcription: str) -> str:
        """Analyze transcription to determine document type"""
        
        analysis_prompt = f"""
        以下の文字起こしを分析して、作成すべき文書の種類を決定してください。
        選択肢: flyer, announcement, notice, event
        
        文字起こし: "{transcription}"
        
        文書の種類のみを返答してください。
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
            logger.warning(f"文書タイプの分析が失敗しました: {e}、デフォルトを使用します")
            return "flyer"
    
    def _build_system_prompt(self, document_type: str) -> str:
        """Build system prompt for document generation"""
        
        base_prompt = """
        あなたは高品質な印刷物を作成するプロフェッショナルな文書デザイナーです。
        見た目が魅力的で、明確で効果的なコンテンツを生成してください。
        すべての回答は日本語で行ってください。
        """
        
        type_specific = {
            "flyer": "明確な階層構造と説得力のある行動喚起を含む、人目を引くフライヤーを作成してください。",
            "announcement": "重要な情報を目立つように配置した、正式なお知らせを作成してください。",
            "notice": "重要な情報を素早く読み取れる、明確な通知を作成してください。",
            "event": "必要な詳細情報をすべて含む、魅力的なイベント招待状を作成してください。"
        }
        
        return f"{base_prompt}\n\n{type_specific.get(document_type, type_specific['flyer'])}"
    
    def _build_user_prompt(self, transcription: str, custom_instructions: Optional[str]) -> str:
        """Build user prompt for document generation"""
        
        prompt = f"""
        以下の音声指示に基づいてプロフェッショナルな文書を作成してください：
        "{transcription}"
        
        {f"追加の指示: {custom_instructions}" if custom_instructions else ""}
        
        以下の正確なJSON形式で回答してください：
        {{
            "title": "文書のタイトル",
            "html": "<div class='document'>HTMLコンテンツをここに</div>",
            "css": ".document {{ CSSスタイルをここに }}"
        }}
        
        要件：
        - プロフェッショナルでモダンなデザイン
        - 明確な階層構造と読みやすさ
        - レスポンシブレイアウト
        - 文字起こしからすべての関連情報を含める
        - 適切なフォント、色、間隔を使用
        - すべてのコンテンツを日本語で生成
        """
        
        return prompt
    
    def _parse_document_response(self, response_content: str) -> Dict[str, str]:
        """Parse GPT response to extract document components"""
        
        try:
            import json
            import re
            
            # Clean up response content by removing markdown code blocks
            cleaned_content = response_content.strip()
            if cleaned_content.startswith('```json'):
                cleaned_content = re.sub(r'^```json\s*', '', cleaned_content)
            if cleaned_content.endswith('```'):
                cleaned_content = re.sub(r'\s*```$', '', cleaned_content)
            
            # Fix common JSON escape issues
            cleaned_content = cleaned_content.replace('\\ ', ' ')  # Fix broken escapes
            cleaned_content = cleaned_content.replace('\\n', '\\n')  # Fix newlines
            cleaned_content = cleaned_content.replace('\\"', '"')   # Fix quotes
            
            # Try to parse as JSON first
            if cleaned_content.strip().startswith('{'):
                content = json.loads(cleaned_content)
                
                # Clean up HTML and CSS content
                html_content = content.get("html", "<div>Content not generated</div>")
                css_content = content.get("css", ".document { font-family: Arial, sans-serif; }")
                
                # Remove ALL unnecessary escaping completely
                html_content = self._clean_content(html_content)
                css_content = self._clean_content(css_content)
                
                return {
                    "title": content.get("title", "Generated Document"),
                    "html": html_content,
                    "css": css_content
                }
            
            # Fallback: Extract components manually
            return self._extract_components_manually(response_content)
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSONデコードエラー: {e}")
            logger.warning(f"Cleaned content: {cleaned_content[:300]}...")
            # Use manual extraction as fallback
            return self._extract_components_manually(response_content)
        except Exception as e:
            logger.warning(f"文書レスポンスの解析に失敗しました: {e}")
            logger.warning(f"Raw response content: {response_content[:200]}...")
            return {
                "title": "生成された文書", 
                "html": f"<div class='document'><h1>生成されたコンテンツ</h1><p>{response_content[:500]}</p></div>",
                "css": ".document { font-family: Arial, sans-serif; padding: 20px; }"
            }
    
    def _extract_components_manually(self, content: str) -> Dict[str, str]:
        """Manually extract HTML/CSS components from response"""
        import re
        
        # Extract title from JSON-like content
        title_match = re.search(r'"title":\s*"([^"]+)"', content)
        title = title_match.group(1) if title_match else "Generated Document"
        
        # Extract HTML from JSON-like content  
        html_match = re.search(r'"html":\s*"([^"]+(?:\\.[^"]*)*)"', content)
        if html_match:
            html_part = self._clean_content(html_match.group(1))
        else:
            # Fallback: Look for any HTML tags
            html_start = content.find("<")
            if html_start != -1:
                html_end = content.rfind(">") + 1
                html_part = self._clean_content(content[html_start:html_end])
            else:
                html_part = f"<div class='document'><h1>{title}</h1><p>{content[:300]}</p></div>"
        
        # Extract CSS from JSON-like content
        css_match = re.search(r'"css":\s*"([^"]+(?:\\.[^"]*)*)"', content) 
        if css_match:
            css_part = self._clean_content(css_match.group(1))
        else:
            css_part = ".document { font-family: Arial, sans-serif; padding: 20px; color: #333; }"
        
        return {
            "title": title,
            "html": html_part,
            "css": css_part
        }
    
    def _clean_content(self, content: str) -> str:
        """Completely clean up escaped content"""
        if not content:
            return content
        
        # Remove all types of unnecessary escaping
        cleaned = content
        
        # Fix multiple backslashes
        cleaned = cleaned.replace('\\\\\\\\', '')  # Remove quadruple backslashes
        cleaned = cleaned.replace('\\\\\\', '')    # Remove triple backslashes  
        cleaned = cleaned.replace('\\\\', '')      # Remove double backslashes
        cleaned = cleaned.replace('\\ ', ' ')      # Remove escaped spaces
        
        # Fix quotes and newlines properly
        cleaned = cleaned.replace('\\"', '"')      # Unescape quotes
        cleaned = cleaned.replace('\\n', '\n')     # Convert to actual newlines
        cleaned = cleaned.replace('\\t', '\t')     # Convert to actual tabs
        
        # Remove any remaining single backslashes before normal characters
        import re
        cleaned = re.sub(r'\\([^\\])', r'\1', cleaned)
        
        return cleaned.strip()

# Global service instance
openai_service = OpenAIService()

def get_openai_service() -> OpenAIService:
    """Get OpenAI service instance"""
    return openai_service
