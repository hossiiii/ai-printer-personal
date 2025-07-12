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
    
    async def get_template_suggestions(
        self, 
        document_type: DocumentType,
        content_hints: List[str] = None
    ) -> Dict[str, Any]:
        """Get template suggestions based on document type and content"""
        
        suggestions = {
            DocumentType.MEETING_MINUTES: {
                'structure': [
                    'Meeting title and date',
                    'Attendees list',
                    'Agenda items',
                    'Discussion points',
                    'Action items with owners',
                    'Next meeting date'
                ],
                'variables': [
                    'meeting_title', 'meeting_date', 'attendees',
                    'agenda_items', 'discussion_points', 'action_items',
                    'next_meeting_date', 'meeting_organizer'
                ],
                'sample_template': '''# {{ meeting_title }}
**Date:** {{ format_date(meeting_date) }}
**Attendees:** {{ attendees | join(", ") }}

## Agenda
{% for item in agenda_items %}
- {{ item }}
{% endfor %}

## Discussion Points
{{ discussion_points }}

## Action Items
{% for action in action_items %}
- [ ] {{ action.task }} ({{ action.owner }})
{% endfor %}

**Next Meeting:** {{ format_date(next_meeting_date) }}'''
            },
            
            DocumentType.LETTER: {
                'structure': [
                    'Sender information',
                    'Date',
                    'Recipient information',
                    'Salutation',
                    'Body paragraphs',
                    'Closing',
                    'Signature'
                ],
                'variables': [
                    'sender_name', 'sender_address', 'recipient_name',
                    'recipient_address', 'date', 'subject', 'body',
                    'closing', 'signature'
                ],
                'sample_template': '''{{ sender_name }}
{{ sender_address }}

{{ format_date(date) }}

{{ recipient_name }}
{{ recipient_address }}

Dear {{ recipient_name }},

{{ body }}

{{ closing }},

{{ signature }}'''
            },
            
            DocumentType.FLYER: {
                'structure': [
                    'Eye-catching headline',
                    'Event details',
                    'Location and time',
                    'Contact information',
                    'Call to action'
                ],
                'variables': [
                    'headline', 'event_name', 'event_date', 'event_time',
                    'location', 'description', 'contact_info', 'call_to_action'
                ],
                'sample_template': '''# {{ headline }}

## {{ event_name }}

**When:** {{ format_date(event_date) }} at {{ event_time }}
**Where:** {{ location }}

{{ description }}

{{ contact_info }}

{{ call_to_action }}'''
            }
        }
        
        return suggestions.get(document_type, {
            'structure': ['Title', 'Content', 'Conclusion'],
            'variables': ['title', 'content'],
            'sample_template': '# {{ title }}\n\n{{ content }}'
        })