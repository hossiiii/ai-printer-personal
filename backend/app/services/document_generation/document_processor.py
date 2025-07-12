"""
Advanced document processing and generation service
"""
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import logging
from datetime import datetime
import re
from dataclasses import dataclass
from ..openai_service import OpenAIService
from .template_engine import AdvancedTemplateEngine, DocumentTemplate
from ...database.models import DocumentType, Document, Template
from ...database.connection import get_db_context
from ...config import settings

logger = logging.getLogger(__name__)


@dataclass
class DocumentGenerationRequest:
    """Document generation request parameters"""
    transcription_text: str
    document_type: DocumentType
    template_id: Optional[int] = None
    custom_template: Optional[str] = None
    style_preferences: Dict[str, Any] = None
    additional_context: Dict[str, Any] = None
    target_length: Optional[str] = None  # short, medium, long
    formality_level: Optional[str] = None  # casual, formal, professional


@dataclass
class DocumentGenerationResult:
    """Document generation result"""
    document_content: str
    formatted_content: str
    metadata: Dict[str, Any]
    quality_score: float
    suggestions: List[str]
    template_variables: Dict[str, Any]


class AdvancedDocumentProcessor:
    """Advanced document processor with AI-powered content generation"""
    
    def __init__(self, openai_service: OpenAIService):
        self.openai_service = openai_service
        self.template_engine = AdvancedTemplateEngine()
        
        # AI prompts for different document types
        self.generation_prompts = {
            DocumentType.MEETING_MINUTES: self._get_meeting_minutes_prompt(),
            DocumentType.LETTER: self._get_letter_prompt(),
            DocumentType.REPORT: self._get_report_prompt(),
            DocumentType.ANNOUNCEMENT: self._get_announcement_prompt(),
            DocumentType.FLYER: self._get_flyer_prompt(),
            DocumentType.CUSTOM: self._get_custom_prompt()
        }
    
    async def generate_document(
        self,
        request: DocumentGenerationRequest,
        user_id: Optional[int] = None
    ) -> DocumentGenerationResult:
        """Generate document from transcription using AI and templates"""
        
        try:
            # Step 1: Analyze transcription and extract key information
            logger.info("Analyzing transcription content...")
            analysis_result = await self._analyze_transcription(
                request.transcription_text,
                request.document_type
            )
            
            # Step 2: Generate structured content using AI
            logger.info("Generating structured content...")
            structured_content = await self._generate_structured_content(
                request, analysis_result
            )
            
            # Step 3: Apply template if specified
            logger.info("Applying document template...")
            formatted_content = await self._apply_template(
                request, structured_content, user_id
            )
            
            # Step 4: Post-process and validate
            logger.info("Post-processing document...")
            final_result = await self._post_process_document(
                structured_content, formatted_content, request
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Document generation failed: {e}")
            raise
    
    async def _analyze_transcription(
        self,
        transcription: str,
        document_type: DocumentType
    ) -> Dict[str, Any]:
        """Analyze transcription to extract key information"""
        
        analysis_prompt = f"""
        Analyze the following transcription and extract key information for generating a {document_type.value}.
        
        Transcription:
        {transcription}
        
        Please extract:
        1. Main topics and themes
        2. Key participants (if mentioned)
        3. Important dates and times
        4. Action items or decisions
        5. Contact information
        6. Tone and formality level
        7. Document structure suggestions
        
        Return the analysis in JSON format with the following structure:
        {{
            "main_topics": ["topic1", "topic2"],
            "participants": ["person1", "person2"],
            "dates_times": ["date1", "time1"],
            "action_items": ["action1", "action2"],
            "contact_info": ["email", "phone"],
            "tone": "formal/casual/professional",
            "structure_suggestions": ["section1", "section2"],
            "key_points": ["point1", "point2"],
            "document_title_suggestions": ["title1", "title2"]
        }}
        """
        
        try:
            response = await self.openai_service.generate_completion(
                analysis_prompt,
                model=settings.OPENAI_MODEL,
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse JSON response
            import json
            analysis = json.loads(response)
            return analysis
            
        except Exception as e:
            logger.warning(f"Analysis failed, using basic extraction: {e}")
            # Fallback to simple extraction
            return {
                "main_topics": self._extract_topics_simple(transcription),
                "participants": self._extract_participants_simple(transcription),
                "dates_times": self._extract_dates_simple(transcription),
                "action_items": [],
                "contact_info": [],
                "tone": "professional",
                "structure_suggestions": ["Introduction", "Main Content", "Conclusion"],
                "key_points": [transcription[:200] + "..."],
                "document_title_suggestions": [f"{document_type.value.title()} Document"]
            }
    
    async def _generate_structured_content(
        self,
        request: DocumentGenerationRequest,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate structured content using AI"""
        
        # Get document-specific prompt
        base_prompt = self.generation_prompts[request.document_type]
        
        # Customize prompt based on request parameters
        style_instructions = self._build_style_instructions(request)
        
        generation_prompt = f"""
        {base_prompt}
        
        Source transcription:
        {request.transcription_text}
        
        Analysis results:
        {analysis}
        
        Style requirements:
        {style_instructions}
        
        Generate a well-structured {request.document_type.value} with:
        1. Appropriate formatting
        2. Clear sections and headers
        3. Professional language
        4. All key information included
        5. Proper document structure for the type
        
        Return the result in JSON format with:
        {{
            "title": "Document title",
            "sections": [
                {{
                    "heading": "Section heading",
                    "content": "Section content"
                }}
            ],
            "metadata": {{
                "word_count": 123,
                "estimated_reading_time": "2 minutes",
                "formality_level": "professional"
            }},
            "template_variables": {{
                "variable_name": "value"
            }}
        }}
        """
        
        try:
            response = await self.openai_service.generate_completion(
                generation_prompt,
                model=settings.OPENAI_MODEL,
                temperature=0.4,
                max_tokens=2000
            )
            
            import json
            structured_content = json.loads(response)
            return structured_content
            
        except Exception as e:
            logger.error(f"Structured content generation failed: {e}")
            # Return basic structure
            return {
                "title": f"{request.document_type.value.title()} Document",
                "sections": [
                    {
                        "heading": "Content",
                        "content": request.transcription_text
                    }
                ],
                "metadata": {
                    "word_count": len(request.transcription_text.split()),
                    "estimated_reading_time": f"{max(1, len(request.transcription_text.split()) // 200)} minutes",
                    "formality_level": "professional"
                },
                "template_variables": {
                    "title": f"{request.document_type.value.title()} Document",
                    "content": request.transcription_text,
                    "date": datetime.now().strftime("%B %d, %Y")
                }
            }
    
    async def _apply_template(
        self,
        request: DocumentGenerationRequest,
        structured_content: Dict[str, Any],
        user_id: Optional[int]
    ) -> str:
        """Apply template to structured content"""
        
        template_variables = structured_content.get("template_variables", {})
        
        # Add additional variables from request
        if request.additional_context:
            template_variables.update(request.additional_context)
        
        try:
            if request.custom_template:
                # Use custom template
                formatted_content = await self.template_engine.render_template(
                    template_content=request.custom_template,
                    variables=template_variables
                )
            elif request.template_id:
                # Use specific template by ID
                formatted_content = await self.template_engine.render_template(
                    template_id=request.template_id,
                    variables=template_variables
                )
            else:
                # Use default template for document type
                formatted_content = await self.template_engine.render_template(
                    document_type=request.document_type,
                    variables=template_variables
                )
            
            return formatted_content
            
        except Exception as e:
            logger.warning(f"Template application failed, using basic formatting: {e}")
            # Fallback to basic formatting
            return self._format_basic_document(structured_content)
    
    async def _post_process_document(
        self,
        structured_content: Dict[str, Any],
        formatted_content: str,
        request: DocumentGenerationRequest
    ) -> DocumentGenerationResult:
        """Post-process document and calculate quality metrics"""
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            structured_content, formatted_content, request
        )
        
        # Generate suggestions for improvement
        suggestions = await self._generate_suggestions(
            structured_content, formatted_content, request
        )
        
        # Extract metadata
        metadata = {
            **structured_content.get("metadata", {}),
            "generation_timestamp": datetime.now().isoformat(),
            "document_type": request.document_type.value,
            "template_used": request.template_id is not None or request.custom_template is not None,
            "processing_version": "2.0"
        }
        
        return DocumentGenerationResult(
            document_content=self._extract_plain_content(structured_content),
            formatted_content=formatted_content,
            metadata=metadata,
            quality_score=quality_score,
            suggestions=suggestions,
            template_variables=structured_content.get("template_variables", {})
        )
    
    def _build_style_instructions(self, request: DocumentGenerationRequest) -> str:
        """Build style instructions from request parameters"""
        instructions = []
        
        if request.target_length:
            length_map = {
                "short": "Keep it concise and to the point",
                "medium": "Provide moderate detail and explanation",
                "long": "Include comprehensive details and explanations"
            }
            instructions.append(length_map.get(request.target_length, ""))
        
        if request.formality_level:
            formality_map = {
                "casual": "Use conversational, friendly language",
                "formal": "Use formal, traditional business language",
                "professional": "Use professional, clear, and direct language"
            }
            instructions.append(formality_map.get(request.formality_level, ""))
        
        if request.style_preferences:
            for key, value in request.style_preferences.items():
                instructions.append(f"{key}: {value}")
        
        return "; ".join(instructions) if instructions else "Use clear, professional language"
    
    def _format_basic_document(self, structured_content: Dict[str, Any]) -> str:
        """Format document using basic formatting when template fails"""
        title = structured_content.get("title", "Document")
        sections = structured_content.get("sections", [])
        
        content_parts = [f"# {title}", ""]
        
        for section in sections:
            heading = section.get("heading", "")
            content = section.get("content", "")
            
            if heading:
                content_parts.append(f"## {heading}")
                content_parts.append("")
            
            content_parts.append(content)
            content_parts.append("")
        
        return "\n".join(content_parts)
    
    def _extract_plain_content(self, structured_content: Dict[str, Any]) -> str:
        """Extract plain text content from structured content"""
        sections = structured_content.get("sections", [])
        content_parts = []
        
        for section in sections:
            content = section.get("content", "")
            content_parts.append(content)
        
        return "\n\n".join(content_parts)
    
    def _calculate_quality_score(
        self,
        structured_content: Dict[str, Any],
        formatted_content: str,
        request: DocumentGenerationRequest
    ) -> float:
        """Calculate document quality score"""
        score = 0.0
        
        # Content completeness (30%)
        sections = structured_content.get("sections", [])
        if len(sections) >= 3:
            score += 0.3
        elif len(sections) >= 2:
            score += 0.2
        elif len(sections) >= 1:
            score += 0.1
        
        # Word count appropriateness (20%)
        word_count = len(formatted_content.split())
        if 100 <= word_count <= 2000:
            score += 0.2
        elif 50 <= word_count <= 100 or 2000 <= word_count <= 3000:
            score += 0.15
        else:
            score += 0.1
        
        # Structure quality (25%)
        if "title" in structured_content and structured_content["title"]:
            score += 0.1
        if len(sections) > 0 and all(s.get("heading") for s in sections):
            score += 0.15
        
        # Template usage (15%)
        if request.template_id or request.custom_template:
            score += 0.15
        else:
            score += 0.05
        
        # Content relevance (10%)
        # Simple heuristic: check if transcription content is reflected
        transcription_words = set(request.transcription_text.lower().split())
        content_words = set(formatted_content.lower().split())
        overlap = len(transcription_words.intersection(content_words))
        if overlap > len(transcription_words) * 0.3:
            score += 0.1
        elif overlap > len(transcription_words) * 0.1:
            score += 0.05
        
        return min(1.0, score)
    
    async def _generate_suggestions(
        self,
        structured_content: Dict[str, Any],
        formatted_content: str,
        request: DocumentGenerationRequest
    ) -> List[str]:
        """Generate suggestions for document improvement"""
        suggestions = []
        
        # Analyze word count
        word_count = len(formatted_content.split())
        if word_count < 50:
            suggestions.append("Consider adding more detail to make the document more comprehensive")
        elif word_count > 2000:
            suggestions.append("Consider condensing the content for better readability")
        
        # Check structure
        sections = structured_content.get("sections", [])
        if len(sections) < 2:
            suggestions.append("Add more sections to improve document structure")
        
        # Check for specific document type requirements
        if request.document_type == DocumentType.MEETING_MINUTES:
            if not any("action" in s.get("heading", "").lower() for s in sections):
                suggestions.append("Consider adding an action items section")
        
        elif request.document_type == DocumentType.LETTER:
            if not any("dear" in formatted_content.lower() or "hello" in formatted_content.lower()):
                suggestions.append("Consider adding a proper salutation")
        
        return suggestions
    
    # Document type specific prompts
    def _get_meeting_minutes_prompt(self) -> str:
        return """
        Generate professional meeting minutes that include:
        - Meeting title, date, and attendees
        - Agenda items discussed
        - Key decisions made
        - Action items with assigned owners
        - Next steps and follow-up dates
        Use clear, concise language appropriate for business documentation.
        """
    
    def _get_letter_prompt(self) -> str:
        return """
        Generate a formal letter that includes:
        - Proper header with sender and recipient information
        - Appropriate salutation
        - Clear, well-structured body paragraphs
        - Professional closing
        - Signature line
        Maintain appropriate formality and business etiquette.
        """
    
    def _get_report_prompt(self) -> str:
        return """
        Generate a comprehensive report that includes:
        - Executive summary
        - Clear sections with descriptive headings
        - Data and findings presentation
        - Analysis and insights
        - Conclusions and recommendations
        Use professional language and logical structure.
        """
    
    def _get_announcement_prompt(self) -> str:
        return """
        Generate a clear announcement that includes:
        - Attention-grabbing headline
        - Important details (what, when, where, who)
        - Clear call to action
        - Contact information if needed
        Use engaging but professional language.
        """
    
    def _get_flyer_prompt(self) -> str:
        return """
        Generate an engaging flyer that includes:
        - Eye-catching headline
        - Event or product details
        - Date, time, and location
        - Benefits or highlights
        - Clear call to action
        - Contact information
        Use persuasive, engaging language appropriate for marketing.
        """
    
    def _get_custom_prompt(self) -> str:
        return """
        Generate a well-structured document based on the content provided.
        Organize information logically with appropriate headings and sections.
        Use clear, professional language suitable for the intended audience.
        """
    
    # Simple extraction methods for fallback
    def _extract_topics_simple(self, text: str) -> List[str]:
        """Simple topic extraction using keyword frequency"""
        # This is a simplified version - in production you'd use NLP techniques
        words = re.findall(r'\b\w+\b', text.lower())
        # Return most common non-stopwords (simplified)
        common_words = ['meeting', 'project', 'team', 'discussion', 'plan']
        return [word for word in common_words if word in words][:5]
    
    def _extract_participants_simple(self, text: str) -> List[str]:
        """Simple participant extraction using capitalized words"""
        # Look for capitalized words that might be names
        potential_names = re.findall(r'\b[A-Z][a-z]+\b', text)
        return list(set(potential_names))[:10]
    
    def _extract_dates_simple(self, text: str) -> List[str]:
        """Simple date extraction using regex patterns"""
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',
            r'\b[A-Za-z]+ \d{1,2}, \d{4}\b'
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text))
        return dates[:5]