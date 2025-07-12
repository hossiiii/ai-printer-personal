"""
Tests for Japanese template system
"""
import pytest
from app.services.document_generation.japanese_templates import (
    JapaneseTemplateLibrary,
    TemplateStyle,
    JapaneseTemplate
)
from app.services.document_generation.template_engine import AdvancedTemplateEngine
from app.database.models import DocumentType


@pytest.fixture
def template_library():
    """Create a template library for testing"""
    return JapaneseTemplateLibrary()


@pytest.fixture
def template_engine():
    """Create a template engine for testing"""
    return AdvancedTemplateEngine()


class TestJapaneseTemplateLibrary:
    """Test Japanese template library functionality"""
    
    def test_library_initialization(self, template_library):
        """Test that library initializes with templates"""
        assert len(template_library.templates) > 0
        assert any(t.document_type == DocumentType.MEETING_MINUTES for t in template_library.templates)
        assert any(t.document_type == DocumentType.LETTER for t in template_library.templates)
        assert any(t.document_type == DocumentType.REPORT for t in template_library.templates)
        assert any(t.document_type == DocumentType.FLYER for t in template_library.templates)
    
    def test_get_templates_by_type(self, template_library):
        """Test filtering templates by document type"""
        meeting_templates = template_library.get_templates_by_type(DocumentType.MEETING_MINUTES)
        assert len(meeting_templates) >= 3  # Professional, Modern, Minimal
        
        letter_templates = template_library.get_templates_by_type(DocumentType.LETTER)
        assert len(letter_templates) >= 2  # Formal, Modern
        
        for template in meeting_templates:
            assert template.document_type == DocumentType.MEETING_MINUTES
    
    def test_get_template_by_id(self, template_library):
        """Test getting specific template by ID"""
        template = template_library.get_template_by_id("meeting_professional_ja")
        assert template.id == "meeting_professional_ja"
        assert template.document_type == DocumentType.MEETING_MINUTES
        assert template.style == TemplateStyle.PROFESSIONAL
        
        # Test non-existent template
        with pytest.raises(ValueError):
            template_library.get_template_by_id("non_existent_template")
    
    def test_get_templates_by_style(self, template_library):
        """Test filtering templates by style"""
        professional_templates = template_library.get_templates_by_style(TemplateStyle.PROFESSIONAL)
        assert len(professional_templates) >= 3
        
        modern_templates = template_library.get_templates_by_style(TemplateStyle.MODERN)
        assert len(modern_templates) >= 3
        
        for template in professional_templates:
            assert template.style == TemplateStyle.PROFESSIONAL
    
    def test_template_properties(self, template_library):
        """Test that all templates have required properties"""
        for template in template_library.templates:
            assert template.id
            assert template.name
            assert template.description
            assert template.css_styles
            assert template.template_html
            assert template.variables
            assert template.category
            assert template.tags
            assert isinstance(template.document_type, DocumentType)
            assert isinstance(template.style, TemplateStyle)
    
    def test_japanese_content(self, template_library):
        """Test that templates contain Japanese content"""
        for template in template_library.templates:
            # Check that template names and descriptions contain Japanese characters
            assert any('\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF' or '\u4E00' <= char <= '\u9FAF' 
                      for char in template.name)
            assert any('\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF' or '\u4E00' <= char <= '\u9FAF' 
                      for char in template.description)


class TestTemplateStyles:
    """Test template CSS styles"""
    
    def test_professional_style_properties(self, template_library):
        """Test professional style properties"""
        template = template_library.get_template_by_id("meeting_professional_ja")
        css = template.css_styles
        
        # Check for Japanese fonts
        assert "Hiragino" in css or "Yu Gothic" in css or "Meiryo" in css
        
        # Check for proper styling elements
        assert "line-height" in css
        assert "color" in css
        assert "margin" in css
        assert "padding" in css
    
    def test_modern_style_properties(self, template_library):
        """Test modern style properties"""
        template = template_library.get_template_by_id("meeting_modern_ja")
        css = template.css_styles
        
        # Check for modern design elements
        assert "gradient" in css.lower()
        assert "border-radius" in css
        assert "box-shadow" in css
    
    def test_formal_style_properties(self, template_library):
        """Test formal style properties"""
        template = template_library.get_template_by_id("letter_formal_ja")
        css = template.css_styles
        
        # Check for formal styling
        assert "serif" in css.lower()
        assert "border" in css
        assert "text-align" in css


class TestTemplateRendering:
    """Test template rendering functionality"""
    
    @pytest.mark.asyncio
    async def test_meeting_template_rendering(self, template_engine):
        """Test rendering meeting minutes template"""
        sample_data = {
            'meeting_title': 'テスト会議',
            'meeting_date': '2024-07-12',
            'attendees': ['田中', '佐藤', '鈴木'],
            'agenda_items': ['議題1', '議題2'],
            'discussion_points': 'テスト討議内容',
            'action_items': [
                {'task': 'タスク1', 'owner': '田中', 'due_date': '2024-07-20'},
                {'task': 'タスク2', 'owner': '佐藤', 'due_date': None}
            ],
            'meeting_organizer': '山田'
        }
        
        # Test with direct template content
        library = JapaneseTemplateLibrary()
        template = library.get_template_by_id("meeting_professional_ja")
        
        rendered = await template_engine.render_template(
            template_content=template.template_html,
            variables=sample_data
        )
        
        assert 'テスト会議' in rendered
        assert '田中' in rendered
        assert '議題1' in rendered
        assert '2024年7月12日' in rendered
    
    @pytest.mark.asyncio
    async def test_letter_template_rendering(self, template_engine):
        """Test rendering letter template"""
        sample_data = {
            'sender_name': '山田太郎',
            'sender_company': '株式会社テスト',
            'recipient_name': '田中次郎',
            'recipient_company': '株式会社サンプル',
            'date': '2024-07-12',
            'subject': 'お礼のご挨拶',
            'body': 'いつもお世話になっております。'
        }
        
        library = JapaneseTemplateLibrary()
        template = library.get_template_by_id("letter_formal_ja")
        
        rendered = await template_engine.render_template(
            template_content=template.template_html,
            variables=sample_data
        )
        
        assert '山田太郎' in rendered
        assert 'お礼のご挨拶' in rendered
        assert '2024年7月12日' in rendered
        assert '拝啓' in rendered
    
    def test_template_variable_extraction(self, template_library):
        """Test that template variables are properly defined"""
        meeting_template = template_library.get_template_by_id("meeting_professional_ja")
        required_vars = ['meeting_title', 'meeting_date', 'attendees', 'agenda_items']
        
        for var in required_vars:
            assert var in meeting_template.variables
        
        letter_template = template_library.get_template_by_id("letter_formal_ja")
        letter_vars = ['sender_name', 'recipient_name', 'subject', 'body']
        
        for var in letter_vars:
            assert var in letter_template.variables


class TestTemplateCategories:
    """Test template categorization"""
    
    def test_template_categories(self, template_library):
        """Test that templates are properly categorized"""
        categories = set(t.category for t in template_library.templates)
        
        expected_categories = {
            "会議・ミーティング",
            "手紙・文書", 
            "レポート・報告書",
            "フライヤー・チラシ"
        }
        
        for category in expected_categories:
            assert category in categories
    
    def test_template_tags(self, template_library):
        """Test that templates have appropriate tags"""
        for template in template_library.templates:
            assert len(template.tags) > 0
            
        # Check specific tags exist
        all_tags = set()
        for template in template_library.templates:
            all_tags.update(template.tags)
        
        expected_tags = {"ビジネス", "プロフェッショナル", "モダン", "フォーマル"}
        for tag in expected_tags:
            assert tag in all_tags


if __name__ == "__main__":
    pytest.main([__file__])