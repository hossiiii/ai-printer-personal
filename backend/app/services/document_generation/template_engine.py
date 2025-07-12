"""
Advanced template engine for document generation
"""
from typing import Dict, Any, List, Optional
from jinja2 import Environment, BaseLoader, TemplateNotFound, select_autoescape
from dataclasses import dataclass
from datetime import datetime
import re
import logging
from ...database.models import Template, DocumentType
from ...database.connection import get_db_context

logger = logging.getLogger(__name__)


@dataclass
class TemplateVariable:
    """Template variable definition"""
    name: str
    type: str  # text, number, date, boolean, list
    description: str
    required: bool = True
    default_value: Any = None
    validation_pattern: Optional[str] = None


@dataclass
class DocumentTemplate:
    """Complete document template definition"""
    id: Optional[int]
    name: str
    description: str
    document_type: DocumentType
    template_content: str
    variables: List[TemplateVariable]
    style_settings: Dict[str, Any]
    is_default: bool = False
    user_id: Optional[int] = None


class DatabaseTemplateLoader(BaseLoader):
    """Custom Jinja2 loader for database-stored templates"""
    
    def __init__(self, user_id: Optional[int] = None):
        self.user_id = user_id
    
    def get_source(self, environment, template):
        """Load template from database"""
        # Template format: "template_type:template_name" or just "template_id"
        try:
            if ':' in template:
                doc_type_str, template_name = template.split(':', 1)
                doc_type = DocumentType(doc_type_str)
                template_obj = self._get_template_by_type_and_name(doc_type, template_name)
            else:
                template_id = int(template)
                template_obj = self._get_template_by_id(template_id)
            
            if not template_obj:
                raise TemplateNotFound(template)
            
            # Return source, filename, uptodate function
            return template_obj.template_content, template, lambda: True
            
        except Exception as e:
            logger.error(f"Failed to load template {template}: {e}")
            raise TemplateNotFound(template)
    
    def _get_template_by_id(self, template_id: int) -> Optional[Template]:
        """Get template by ID"""
        # This would normally be async, but Jinja2 loader is sync
        # In practice, you'd cache templates or use a different approach
        pass
    
    def _get_template_by_type_and_name(self, doc_type: DocumentType, name: str) -> Optional[Template]:
        """Get template by type and name"""
        pass


class AdvancedTemplateEngine:
    """Advanced template engine with custom functions and filters"""
    
    def __init__(self, user_id: Optional[int] = None):
        self.user_id = user_id
        self.env = self._create_environment()
        self._register_custom_functions()
        self._register_custom_filters()
    
    def _create_environment(self) -> Environment:
        """Create Jinja2 environment with custom loader"""
        env = Environment(
            loader=DatabaseTemplateLoader(self.user_id),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        return env
    
    def _register_custom_functions(self):
        """Register custom functions for templates"""
        
        def format_date(date_str: str, format_pattern: str = "%B %d, %Y") -> str:
            """Format date string"""
            try:
                if isinstance(date_str, str):
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    date_obj = date_str
                return date_obj.strftime(format_pattern)
            except:
                return date_str
        
        def current_date(format_pattern: str = "%B %d, %Y") -> str:
            """Get current date formatted"""
            return datetime.now().strftime(format_pattern)
        
        def format_currency(amount: float, currency: str = "USD") -> str:
            """Format currency amount"""
            if currency == "USD":
                return f"${amount:,.2f}"
            elif currency == "EUR":
                return f"€{amount:,.2f}"
            else:
                return f"{amount:,.2f} {currency}"
        
        def create_list(items: str, separator: str = ",") -> List[str]:
            """Create list from separated string"""
            return [item.strip() for item in items.split(separator) if item.strip()]
        
        def format_phone(phone: str) -> str:
            """Format phone number"""
            # Remove all non-digit characters
            digits = re.sub(r'\D', '', phone)
            if len(digits) == 10:
                return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits[0] == '1':
                return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            return phone
        
        def word_count(text: str) -> int:
            """Count words in text"""
            return len(text.split())
        
        def truncate_words(text: str, word_limit: int, suffix: str = "...") -> str:
            """Truncate text to word limit"""
            words = text.split()
            if len(words) <= word_limit:
                return text
            return " ".join(words[:word_limit]) + suffix
        
        # Register functions as globals
        self.env.globals.update({
            'format_date': format_date,
            'current_date': current_date,
            'format_currency': format_currency,
            'create_list': create_list,
            'format_phone': format_phone,
            'word_count': word_count,
            'truncate_words': truncate_words,
        })
    
    def _register_custom_filters(self):
        """Register custom filters for templates"""
        
        def title_case(text: str) -> str:
            """Convert to title case with proper handling of articles"""
            articles = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from', 'by'}
            words = text.lower().split()
            if not words:
                return text
            
            # Always capitalize first word
            result = [words[0].capitalize()]
            
            for word in words[1:]:
                if word in articles:
                    result.append(word)
                else:
                    result.append(word.capitalize())
            
            return ' '.join(result)
        
        def currency(amount: float, currency_code: str = "USD") -> str:
            """Format as currency"""
            return self.env.globals['format_currency'](amount, currency_code)
        
        def phone(phone_number: str) -> str:
            """Format phone number"""
            return self.env.globals['format_phone'](phone_number)
        
        def markdown_to_html(text: str) -> str:
            """Convert basic markdown to HTML"""
            # Basic markdown conversion
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
            text = re.sub(r'\n\n', '</p><p>', text)
            text = f'<p>{text}</p>'
            text = re.sub(r'<p></p>', '', text)
            return text
        
        def bullet_list(items: List[str], bullet_char: str = "•") -> str:
            """Create bullet list HTML"""
            if not items:
                return ""
            list_items = [f"<li>{item}</li>" for item in items]
            return f"<ul>{''.join(list_items)}</ul>"
        
        def numbered_list(items: List[str]) -> str:
            """Create numbered list HTML"""
            if not items:
                return ""
            list_items = [f"<li>{item}</li>" for item in items]
            return f"<ol>{''.join(list_items)}</ol>"
        
        # Register filters
        self.env.filters.update({
            'title_case': title_case,
            'currency': currency,
            'phone': phone,
            'markdown': markdown_to_html,
            'bullets': bullet_list,
            'numbered': numbered_list,
        })
    
    async def render_template(
        self,
        template_id: Optional[int] = None,
        template_content: Optional[str] = None,
        variables: Dict[str, Any] = None,
        document_type: Optional[DocumentType] = None
    ) -> str:
        """Render template with provided variables"""
        
        variables = variables or {}
        
        try:
            if template_content:
                # Use provided template content directly
                template = self.env.from_string(template_content)
            elif template_id:
                # Load template from database by ID
                template = self.env.get_template(str(template_id))
            elif document_type:
                # Load default template for document type
                template = self.env.get_template(f"{document_type.value}:default")
            else:
                raise ValueError("Must provide template_id, template_content, or document_type")
            
            # Add common variables
            common_vars = {
                'current_date': datetime.now().strftime("%B %d, %Y"),
                'current_time': datetime.now().strftime("%I:%M %p"),
                'current_year': datetime.now().year,
            }
            
            # Merge variables
            render_vars = {**common_vars, **variables}
            
            # Render template
            rendered = template.render(**render_vars)
            
            return rendered
            
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            raise
    
    async def validate_template(self, template_content: str) -> Dict[str, Any]:
        """Validate template syntax and extract variables"""
        
        try:
            # Parse template to check syntax
            template = self.env.from_string(template_content)
            
            # Extract undefined variables
            from jinja2.meta import find_undeclared_variables
            ast = self.env.parse(template_content)
            undefined_vars = find_undeclared_variables(ast)
            
            # Try to render with empty context to find required variables
            try:
                template.render()
                required_vars = []
            except Exception as render_error:
                # Extract variable names from error message
                error_msg = str(render_error)
                required_vars = list(undefined_vars)
            
            return {
                'valid': True,
                'undefined_variables': list(undefined_vars),
                'required_variables': required_vars,
                'syntax_errors': []
            }
            
        except Exception as e:
            return {
                'valid': False,
                'undefined_variables': [],
                'required_variables': [],
                'syntax_errors': [str(e)]
            }
    
    def get_japanese_template_styles(self) -> Dict[str, str]:
        """Get CSS styles optimized for Japanese documents"""
        return {
            'japanese_professional': '''
                <style>
                body {
                    font-family: "Hiragino Kaku Gothic ProN", "Hiragino Sans", "Yu Gothic Medium", "Meiryo", "MS Gothic", sans-serif;
                    font-size: 14px;
                    line-height: 1.8;
                    color: #1e293b;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 40px 32px;
                    background: white;
                }
                
                h1 {
                    font-size: 24px;
                    font-weight: 600;
                    color: #1e293b;
                    text-align: center;
                    margin-bottom: 32px;
                    padding-bottom: 16px;
                    border-bottom: 2px solid #22c55e;
                }
                
                h2 {
                    font-size: 18px;
                    font-weight: 600;
                    color: #334155;
                    margin: 32px 0 16px 0;
                    padding: 8px 16px;
                    background: linear-gradient(90deg, #f8f9fa, transparent);
                    border-left: 4px solid #22c55e;
                }
                
                h3 {
                    font-size: 16px;
                    font-weight: 600;
                    color: #475569;
                    margin: 24px 0 12px 0;
                }
                
                p {
                    margin: 16px 0;
                    text-align: justify;
                }
                
                .date-header {
                    text-align: right;
                    font-size: 14px;
                    color: #64748b;
                    margin-bottom: 24px;
                }
                
                .sender-info, .recipient-info {
                    margin: 24px 0;
                    padding: 16px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }
                
                .highlight {
                    background: linear-gradient(transparent 60%, rgba(34, 197, 94, 0.3) 60%);
                    padding: 2px 4px;
                }
                
                ul, ol {
                    margin: 16px 0;
                    padding-left: 24px;
                }
                
                li {
                    margin: 8px 0;
                }
                
                .action-item {
                    background: #f1f5f9;
                    padding: 12px;
                    margin: 8px 0;
                    border-radius: 6px;
                    border-left: 3px solid #3b82f6;
                }
                
                .footer {
                    margin-top: 48px;
                    text-align: center;
                    font-size: 12px;
                    color: #94a3b8;
                    border-top: 1px solid #e2e8f0;
                    padding-top: 16px;
                }
                
                @media print {
                    body { padding: 20px; }
                    h1 { border-bottom: 1px solid #000; }
                    .action-item { border: 1px solid #ccc; }
                }
                </style>
            ''',
            
            'japanese_modern': '''
                <style>
                body {
                    font-family: "Hiragino Kaku Gothic ProN", "Hiragino Sans", "Yu Gothic Medium", "Meiryo", sans-serif;
                    font-size: 14px;
                    line-height: 1.7;
                    color: #1e293b;
                    max-width: 750px;
                    margin: 0 auto;
                    padding: 48px 40px;
                    background: linear-gradient(135deg, #fafafa 0%, #ffffff 100%);
                }
                
                h1 {
                    font-size: 28px;
                    font-weight: 700;
                    color: #0f172a;
                    text-align: center;
                    margin-bottom: 40px;
                    position: relative;
                }
                
                h1:after {
                    content: '';
                    position: absolute;
                    bottom: -12px;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 80px;
                    height: 3px;
                    background: linear-gradient(90deg, #22c55e, #ef2b70);
                    border-radius: 2px;
                }
                
                h2 {
                    font-size: 20px;
                    font-weight: 600;
                    color: #1e293b;
                    margin: 36px 0 20px 0;
                    padding: 12px 20px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    border-left: 4px solid #22c55e;
                }
                
                h3 {
                    font-size: 16px;
                    font-weight: 600;
                    color: #334155;
                    margin: 28px 0 16px 0;
                }
                
                p {
                    margin: 18px 0;
                    text-align: justify;
                }
                
                .card {
                    background: white;
                    padding: 24px;
                    margin: 20px 0;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                    border: 1px solid #e2e8f0;
                }
                
                .date-badge {
                    display: inline-block;
                    background: linear-gradient(135deg, #22c55e, #16a34a);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 13px;
                    font-weight: 500;
                    margin-bottom: 20px;
                }
                
                .attendees {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    margin: 16px 0;
                }
                
                .attendee-tag {
                    background: #f1f5f9;
                    color: #475569;
                    padding: 6px 12px;
                    border-radius: 16px;
                    font-size: 13px;
                    border: 1px solid #cbd5e1;
                }
                
                .action-grid {
                    display: grid;
                    gap: 16px;
                    margin: 24px 0;
                }
                
                .action-card {
                    background: #fafafa;
                    padding: 16px;
                    border-radius: 8px;
                    border-left: 4px solid #3b82f6;
                    position: relative;
                }
                
                .action-card:before {
                    content: '📝';
                    position: absolute;
                    right: 16px;
                    top: 16px;
                    font-size: 18px;
                }
                
                @media (max-width: 768px) {
                    body { padding: 24px 20px; }
                    .attendees { flex-direction: column; }
                }
                </style>
            ''',
            
            'japanese_formal': '''
                <style>
                body {
                    font-family: "MS Mincho", "Yu Mincho", "Hiragino Mincho ProN", serif;
                    font-size: 14px;
                    line-height: 1.9;
                    color: #1a1a1a;
                    max-width: 700px;
                    margin: 0 auto;
                    padding: 60px 48px;
                    background: white;
                }
                
                h1 {
                    font-size: 22px;
                    font-weight: 600;
                    color: #1a1a1a;
                    text-align: center;
                    margin-bottom: 48px;
                    padding: 20px 0;
                    border: 2px solid #1a1a1a;
                    position: relative;
                }
                
                h1:before, h1:after {
                    content: '';
                    position: absolute;
                    width: 30px;
                    height: 30px;
                    border: 2px solid #1a1a1a;
                }
                
                h1:before {
                    top: -2px;
                    left: -2px;
                    border-right: none;
                    border-bottom: none;
                }
                
                h1:after {
                    bottom: -2px;
                    right: -2px;
                    border-left: none;
                    border-top: none;
                }
                
                h2 {
                    font-size: 18px;
                    font-weight: 600;
                    color: #1a1a1a;
                    margin: 40px 0 20px 0;
                    text-align: center;
                    padding-bottom: 8px;
                    border-bottom: 1px solid #666;
                }
                
                h3 {
                    font-size: 16px;
                    font-weight: 600;
                    color: #333;
                    margin: 32px 0 16px 0;
                    text-decoration: underline;
                }
                
                p {
                    margin: 20px 0;
                    text-align: justify;
                    text-indent: 1em;
                }
                
                .date-line {
                    text-align: right;
                    font-size: 14px;
                    margin-bottom: 40px;
                    padding-right: 20px;
                }
                
                .formal-address {
                    margin: 30px 0;
                    padding: 20px;
                    border: 1px solid #ccc;
                    text-align: center;
                    background: #fafafa;
                }
                
                .closing-section {
                    margin-top: 60px;
                    text-align: right;
                    padding-right: 40px;
                }
                
                .signature-line {
                    margin-top: 40px;
                    border-bottom: 1px solid #333;
                    width: 200px;
                    margin-left: auto;
                    padding-bottom: 20px;
                }
                
                ul, ol {
                    margin: 20px 0;
                    padding-left: 40px;
                }
                
                li {
                    margin: 12px 0;
                }
                
                .item-box {
                    border: 1px solid #ccc;
                    padding: 16px;
                    margin: 16px 0;
                    background: #f9f9f9;
                }
                
                @media print {
                    body { 
                        padding: 40px;
                        font-size: 12px;
                    }
                }
                </style>
            '''
        }
    
    async def get_template_suggestions(
        self, 
        document_type: DocumentType,
        content_hints: List[str] = None,
        style_preference: str = "japanese_professional"
    ) -> Dict[str, Any]:
        """Get template suggestions based on document type and content with Japanese styling"""
        
        styles = self.get_japanese_template_styles()
        selected_style = styles.get(style_preference, styles['japanese_professional'])
        
        suggestions = {
            DocumentType.MEETING_MINUTES: {
                'structure': [
                    '会議タイトルと日時',
                    '出席者リスト',
                    '議題項目',
                    '討議内容',
                    '決定事項とアクション項目',
                    '次回会議予定'
                ],
                'variables': [
                    'meeting_title', 'meeting_date', 'attendees',
                    'agenda_items', 'discussion_points', 'action_items',
                    'next_meeting_date', 'meeting_organizer'
                ],
                'sample_template': f'''{selected_style}
<div class="date-header">{{ format_date(meeting_date, "%Y年%m月%d日") }}</div>

<h1>{{ meeting_title }}</h1>

<div class="card">
<h2>📋 会議概要</h2>
<p><strong>主催者：</strong>{{ meeting_organizer }}</p>
<div class="attendees">
{% for attendee in attendees %}
<span class="attendee-tag">{{ attendee }}</span>
{% endfor %}
</div>
</div>

<h2>📝 議題</h2>
<ol>
{% for item in agenda_items %}
<li>{{ item }}</li>
{% endfor %}
</ol>

<h2>💬 討議内容</h2>
{{ discussion_points | markdown }}

<h2>✅ アクション項目</h2>
<div class="action-grid">
{% for action in action_items %}
<div class="action-card">
<strong>{{ action.task }}</strong><br>
担当者: {{ action.owner }}<br>
期限: {{ format_date(action.due_date, "%m月%d日") if action.due_date else "未定" }}
</div>
{% endfor %}
</div>

<div class="footer">
次回会議: {{ format_date(next_meeting_date, "%Y年%m月%d日") if next_meeting_date else "未定" }}
</div>'''
            },
            
            DocumentType.LETTER: {
                'structure': [
                    '差出人情報',
                    '日付',
                    '宛先情報',
                    '件名',
                    '本文',
                    '結び',
                    '署名'
                ],
                'variables': [
                    'sender_name', 'sender_title', 'sender_company', 'sender_address',
                    'recipient_name', 'recipient_title', 'recipient_company', 'recipient_address',
                    'date', 'subject', 'body', 'closing', 'signature'
                ],
                'sample_template': f'''{selected_style}
<div class="date-line">{{ format_date(date, "%Y年%m月%d日") }}</div>

<div class="formal-address">
{{ recipient_company }}<br>
{{ recipient_title }} {{ recipient_name }} 様
</div>

<h1>{{ subject }}</h1>

<p>拝啓　時下ますますご清栄のこととお慶び申し上げます。</p>

{{ body | markdown }}

<p>何かご不明な点がございましたら、お気軽にお問い合わせください。</p>

<p>今後ともよろしくお願い申し上げます。</p>

<div class="closing-section">
<p>敬具</p>

<div style="margin-top: 40px;">
{{ sender_company }}<br>
{{ sender_title }}<br>
<strong>{{ sender_name }}</strong>
</div>

{% if sender_address %}
<div style="margin-top: 20px; font-size: 12px; color: #666;">
{{ sender_address }}
</div>
{% endif %}
</div>'''
            },
            
            DocumentType.REPORT: {
                'structure': [
                    'レポートタイトル',
                    '作成日時・作成者',
                    '概要',
                    '詳細内容',
                    '結論・提案',
                    '添付資料'
                ],
                'variables': [
                    'report_title', 'author', 'date', 'summary',
                    'content_sections', 'conclusions', 'recommendations',
                    'attachments'
                ],
                'sample_template': f'''{selected_style}
<div class="date-badge">{{ format_date(date, "%Y年%m月%d日") }}</div>

<h1>{{ report_title }}</h1>

<div class="card">
<h2>📊 概要</h2>
<p><strong>作成者：</strong>{{ author }}</p>
<p><strong>作成日：</strong>{{ format_date(date, "%Y年%m月%d日") }}</p>
{{ summary | markdown }}
</div>

<h2>📋 詳細内容</h2>
{% for section in content_sections %}
<div class="card">
<h3>{{ section.title }}</h3>
{{ section.content | markdown }}
</div>
{% endfor %}

<h2>💡 結論・提案</h2>
<div class="card">
{{ conclusions | markdown }}

{% if recommendations %}
<h3>推奨事項</h3>
<ul>
{% for rec in recommendations %}
<li class="highlight">{{ rec }}</li>
{% endfor %}
</ul>
{% endif %}
</div>

{% if attachments %}
<div class="footer">
<strong>添付資料：</strong>{{ attachments | join(", ") }}
</div>
{% endif %}'''
            },
            
            DocumentType.FLYER: {
                'structure': [
                    'キャッチフレーズ',
                    'イベント詳細',
                    '日時・場所',
                    '連絡先情報',
                    '行動喚起'
                ],
                'variables': [
                    'headline', 'event_name', 'event_date', 'event_time',
                    'location', 'description', 'contact_info', 'call_to_action',
                    'organizer', 'ticket_info'
                ],
                'sample_template': f'''{selected_style}
<h1 style="font-size: 32px; color: #22c55e; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);">
{{ headline }}
</h1>

<div class="card" style="text-align: center; background: linear-gradient(135deg, #f8f9fa, #e2e8f0);">
<h2 style="font-size: 24px; margin-bottom: 24px;">{{ event_name }}</h2>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin: 24px 0;">
<div>
<h3>📅 日時</h3>
<p><strong>{{ format_date(event_date, "%Y年%m月%d日") }}</strong></p>
<p>{{ event_time }}</p>
</div>
<div>
<h3>📍 場所</h3>
<p>{{ location }}</p>
</div>
</div>
</div>

<div class="card">
{{ description | markdown }}
</div>

{% if ticket_info %}
<div class="card" style="background: #fef3c7; border-left-color: #f59e0b;">
<h3>🎫 参加方法</h3>
{{ ticket_info | markdown }}
</div>
{% endif %}

<div class="card" style="background: #dcfce7; border-left-color: #22c55e; text-align: center;">
<h3 style="color: #15803d;">{{ call_to_action }}</h3>
</div>

<div class="footer">
<strong>主催：</strong>{{ organizer }}<br>
<strong>お問い合わせ：</strong>{{ contact_info }}
</div>'''
            }
        }
        
        return suggestions.get(document_type, {
            'structure': ['タイトル', '内容', '結論'],
            'variables': ['title', 'content'],
            'sample_template': f'{selected_style}<h1>{{ title }}</h1>\n\n{{ content | markdown }}'
        })