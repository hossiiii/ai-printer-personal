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
            logger.error(f"文書生成が失敗しました: {e}")
            raise
    
    async def _analyze_transcription(
        self,
        transcription: str,
        document_type: DocumentType
    ) -> Dict[str, Any]:
        """Analyze transcription to extract key information"""
        
        analysis_prompt = f"""
        以下の文字起こしを分析して、{document_type.value}の生成に必要な重要な情報を抽出してください。
        
        文字起こし:
        {transcription}
        
        以下の項目を抽出してください：
        1. 主要なトピックとテーマ
        2. 主要な参加者（言及されている場合）
        3. 重要な日付と時間
        4. アクションアイテムや決定事項
        5. 連絡先情報
        6. 文書のトーンと形式レベル
        7. 文書構造の提案
        
        以下の構造でJSON形式で分析結果を返してください（すべて日本語で）：
        {{
            "main_topics": ["トピック1", "トピック2"],
            "participants": ["参加者1", "参加者2"],
            "dates_times": ["日付1", "時間1"],
            "action_items": ["アクション1", "アクション2"],
            "contact_info": ["メール", "電話"],
            "tone": "formal/casual/professional",
            "structure_suggestions": ["セクション1", "セクション2"],
            "key_points": ["ポイント1", "ポイント2"],
            "document_title_suggestions": ["タイトル1", "タイトル2"]
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
            logger.warning(f"分析が失敗しました、基本的な抽出を使用します: {e}")
            # Fallback to simple extraction
            return {
                "main_topics": self._extract_topics_simple(transcription),
                "participants": self._extract_participants_simple(transcription),
                "dates_times": self._extract_dates_simple(transcription),
                "action_items": [],
                "contact_info": [],
                "tone": "professional",
                "structure_suggestions": ["はじめに", "メインコンテンツ", "まとめ"],
                "key_points": [transcription[:200] + "..."],
                "document_title_suggestions": [f"{document_type.value.title()} 文書"]
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
        
        元の文字起こし:
        {request.transcription_text}
        
        分析結果:
        {analysis}
        
        スタイル要件:
        {style_instructions}
        
        以下の要素を含む、よく構造化された{request.document_type.value}を生成してください：
        1. 適切なフォーマット
        2. 明確なセクションとヘッダー
        3. プロフェッショナルな日本語
        4. すべての重要な情報を含める
        5. 文書タイプに適した構造
        
        以下のJSON形式で結果を返してください（すべて日本語で）：
        {{
            "title": "文書タイトル",
            "sections": [
                {{
                    "heading": "セクション見出し",
                    "content": "セクション内容"
                }}
            ],
            "metadata": {{
                "word_count": 123,
                "estimated_reading_time": "2分",
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
            logger.error(f"構造化コンテンツの生成が失敗しました: {e}")
            # Return basic structure
            return {
                "title": f"{request.document_type.value.title()} 文書",
                "sections": [
                    {
                        "heading": "内容",
                        "content": request.transcription_text
                    }
                ],
                "metadata": {
                    "word_count": len(request.transcription_text.split()),
                    "estimated_reading_time": f"{max(1, len(request.transcription_text.split()) // 200)}分",
                    "formality_level": "professional"
                },
                "template_variables": {
                    "title": f"{request.document_type.value.title()} 文書",
                    "content": request.transcription_text,
                    "date": datetime.now().strftime("%Y年%m月%d日")
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
            logger.warning(f"テンプレートの適用が失敗しました、基本的なフォーマットを使用します: {e}")
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
                "short": "簡潔で要点を絞った内容にしてください",
                "medium": "適度な詳細と説明を提供してください",
                "long": "包括的な詳細と説明を含めてください"
            }
            instructions.append(length_map.get(request.target_length, ""))
        
        if request.formality_level:
            formality_map = {
                "casual": "会話的で親しみやすい日本語を使用してください",
                "formal": "正式で伝統的なビジネス日本語を使用してください",
                "professional": "プロフェッショナルで明確かつ直接的な日本語を使用してください"
            }
            instructions.append(formality_map.get(request.formality_level, ""))
        
        if request.style_preferences:
            for key, value in request.style_preferences.items():
                instructions.append(f"{key}: {value}")
        
        return "；".join(instructions) if instructions else "明確でプロフェッショナルな日本語を使用してください"
    
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
            suggestions.append("文書をより包括的にするために詳細を追加することを検討してください")
        elif word_count > 2000:
            suggestions.append("読みやすさを向上させるためにコンテンツの簡潔化を検討してください")
        
        # Check structure
        sections = structured_content.get("sections", [])
        if len(sections) < 2:
            suggestions.append("文書構造を改善するためにセクションを追加してください")
        
        # Check for specific document type requirements
        if request.document_type == DocumentType.MEETING_MINUTES:
            if not any("アクション" in s.get("heading", "").lower() or "行動" in s.get("heading", "").lower() for s in sections):
                suggestions.append("アクションアイテムのセクションを追加することを検討してください")
        
        elif request.document_type == DocumentType.LETTER:
            if not any("拝啓" in formatted_content or "いつもお世話" in formatted_content or "平素より" in formatted_content):
                suggestions.append("適切な挨拶文を追加することを検討してください")
        
        return suggestions
    
    # Document type specific prompts
    def _get_meeting_minutes_prompt(self) -> str:
        return """
        以下を含むプロフェッショナルな議事録を生成してください：
        - 会議タイトル、日付、参加者
        - 議論されたアジェンダ項目
        - 決定された重要事項
        - 担当者が割り当てられたアクションアイテム
        - 次のステップとフォローアップ日程
        ビジネス文書に適した明確で簡潔な日本語を使用してください。
        """
    
    def _get_letter_prompt(self) -> str:
        return """
        以下を含む正式な手紙を生成してください：
        - 送信者と受信者の情報を含む適切なヘッダー
        - 適切な挨拶
        - 明確で構造化された本文段落
        - プロフェッショナルな結び
        - 署名欄
        適切な敬語とビジネスマナーを維持してください。
        """
    
    def _get_report_prompt(self) -> str:
        return """
        以下を含む包括的な報告書を生成してください：
        - エグゼクティブサマリー
        - 説明的な見出しを持つ明確なセクション
        - データと調査結果の提示
        - 分析と洞察
        - 結論と提案
        プロフェッショナルな日本語と論理的な構造を使用してください。
        """
    
    def _get_announcement_prompt(self) -> str:
        return """
        以下を含む明確なお知らせを生成してください：
        - 注意を引く見出し
        - 重要な詳細（何を、いつ、どこで、誰が）
        - 明確な行動喚起
        - 必要に応じて連絡先情報
        魅力的でプロフェッショナルな日本語を使用してください。
        """
    
    def _get_flyer_prompt(self) -> str:
        return """
        以下を含む魅力的なフライヤーを生成してください：
        - 目を引く見出し
        - イベントや製品の詳細
        - 日付、時間、場所
        - メリットやハイライト
        - 明確な行動喚起
        - 連絡先情報
        マーケティングに適した説得力のある魅力的な日本語を使用してください。
        """
    
    def _get_custom_prompt(self) -> str:
        return """
        提供されたコンテンツに基づいて、よく構造化された文書を生成してください。
        適切な見出しとセクションで情報を論理的に整理してください。
        対象読者に適した明確でプロフェッショナルな日本語を使用してください。
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