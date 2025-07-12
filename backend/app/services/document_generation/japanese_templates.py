"""
Japanese-optimized document templates with improved design
"""
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
from ...database.models import DocumentType


class TemplateStyle(Enum):
    PROFESSIONAL = "japanese_professional"
    MODERN = "japanese_modern"
    FORMAL = "japanese_formal"
    CREATIVE = "japanese_creative"
    MINIMAL = "japanese_minimal"


@dataclass
class JapaneseTemplate:
    """Japanese-optimized template definition"""
    id: str
    name: str
    description: str
    document_type: DocumentType
    style: TemplateStyle
    template_html: str
    css_styles: str
    variables: List[str]
    category: str
    tags: List[str]


class JapaneseTemplateLibrary:
    """Library of Japanese-optimized templates"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _get_base_styles(self) -> Dict[str, str]:
        """Get base CSS styles for different template styles"""
        return {
            TemplateStyle.PROFESSIONAL.value: '''
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
                .card {
                    background: #f8f9fa;
                    padding: 16px;
                    margin: 16px 0;
                    border-radius: 8px;
                    border: 1px solid #e2e8f0;
                }
                .highlight {
                    background: linear-gradient(transparent 60%, rgba(34, 197, 94, 0.3) 60%);
                    padding: 2px 4px;
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
                    body { padding: 20px; font-size: 12px; }
                    h1 { border-bottom: 1px solid #000; }
                }
                </style>
            ''',
            
            TemplateStyle.MODERN.value: '''
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
                .card {
                    background: white;
                    padding: 24px;
                    margin: 20px 0;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                    border: 1px solid #e2e8f0;
                }
                .badge {
                    display: inline-block;
                    background: linear-gradient(135deg, #22c55e, #16a34a);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 13px;
                    font-weight: 500;
                    margin-bottom: 20px;
                }
                .tag {
                    background: #f1f5f9;
                    color: #475569;
                    padding: 6px 12px;
                    border-radius: 16px;
                    font-size: 13px;
                    border: 1px solid #cbd5e1;
                    display: inline-block;
                    margin: 4px;
                }
                @media (max-width: 768px) {
                    body { padding: 24px 20px; }
                }
                </style>
            ''',
            
            TemplateStyle.FORMAL.value: '''
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
                .formal-box {
                    border: 1px solid #ccc;
                    padding: 20px;
                    margin: 30px 0;
                    text-align: center;
                    background: #fafafa;
                }
                .signature-section {
                    margin-top: 60px;
                    text-align: right;
                    padding-right: 40px;
                }
                p {
                    text-indent: 1em;
                }
                @media print {
                    body { padding: 40px; font-size: 12px; }
                }
                </style>
            ''',
            
            TemplateStyle.CREATIVE.value: '''
                <style>
                body {
                    font-family: "Hiragino Kaku Gothic ProN", "Hiragino Sans", "Yu Gothic Medium", sans-serif;
                    font-size: 14px;
                    line-height: 1.6;
                    color: #2d3748;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 40px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }
                .content {
                    background: white;
                    border-radius: 20px;
                    padding: 40px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                }
                h1 {
                    font-size: 32px;
                    font-weight: 800;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    text-align: center;
                    margin-bottom: 40px;
                }
                h2 {
                    font-size: 24px;
                    font-weight: 600;
                    color: #4a5568;
                    margin: 32px 0 16px 0;
                    position: relative;
                    padding-left: 20px;
                }
                h2:before {
                    content: '';
                    position: absolute;
                    left: 0;
                    top: 50%;
                    transform: translateY(-50%);
                    width: 4px;
                    height: 100%;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    border-radius: 2px;
                }
                .creative-card {
                    background: linear-gradient(135deg, #f7fafc, #edf2f7);
                    border-radius: 16px;
                    padding: 24px;
                    margin: 20px 0;
                    border-left: 4px solid #667eea;
                    position: relative;
                    overflow: hidden;
                }
                .creative-card:before {
                    content: '';
                    position: absolute;
                    top: 0;
                    right: 0;
                    width: 100px;
                    height: 100px;
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
                    border-radius: 50%;
                    transform: translate(30px, -30px);
                }
                .emoji-header {
                    font-size: 24px;
                    margin-right: 12px;
                }
                </style>
            ''',
            
            TemplateStyle.MINIMAL.value: '''
                <style>
                body {
                    font-family: "Hiragino Kaku Gothic ProN", "Hiragino Sans", "Yu Gothic", sans-serif;
                    font-size: 15px;
                    line-height: 1.7;
                    color: #2d3748;
                    max-width: 650px;
                    margin: 0 auto;
                    padding: 80px 40px;
                    background: #ffffff;
                }
                h1 {
                    font-size: 28px;
                    font-weight: 300;
                    color: #1a202c;
                    text-align: left;
                    margin-bottom: 60px;
                    letter-spacing: -0.5px;
                }
                h2 {
                    font-size: 20px;
                    font-weight: 400;
                    color: #2d3748;
                    margin: 48px 0 16px 0;
                    letter-spacing: -0.3px;
                }
                h3 {
                    font-size: 16px;
                    font-weight: 500;
                    color: #4a5568;
                    margin: 32px 0 12px 0;
                }
                p {
                    margin: 24px 0;
                    color: #4a5568;
                }
                .minimal-divider {
                    width: 60px;
                    height: 1px;
                    background: #cbd5e0;
                    margin: 40px 0;
                    border: none;
                }
                .minimal-highlight {
                    border-left: 2px solid #e2e8f0;
                    padding-left: 24px;
                    margin: 32px 0;
                    font-style: italic;
                    color: #718096;
                }
                .date-simple {
                    font-size: 13px;
                    color: #a0aec0;
                    margin-bottom: 40px;
                }
                ul, ol {
                    color: #4a5568;
                    margin: 24px 0;
                }
                @media print {
                    body { padding: 40px 20px; }
                }
                </style>
            '''
        }
    
    def _initialize_templates(self) -> List[JapaneseTemplate]:
        """Initialize all Japanese templates"""
        styles = self._get_base_styles()
        
        templates = []
        
        # Meeting Minutes Templates
        templates.extend([
            JapaneseTemplate(
                id="meeting_professional_ja",
                name="会議議事録（プロフェッショナル）",
                description="ビジネス会議に適したプロフェッショナルなデザイン",
                document_type=DocumentType.MEETING_MINUTES,
                style=TemplateStyle.PROFESSIONAL,
                css_styles=styles[TemplateStyle.PROFESSIONAL.value],
                template_html=self._get_meeting_professional_template(),
                variables=['meeting_title', 'meeting_date', 'attendees', 'agenda_items', 'discussion_points', 'action_items', 'next_meeting_date', 'meeting_organizer'],
                category="会議・ミーティング",
                tags=["ビジネス", "プロフェッショナル", "標準"]
            ),
            JapaneseTemplate(
                id="meeting_modern_ja",
                name="会議議事録（モダン）",
                description="モダンで視覚的に魅力的なデザイン",
                document_type=DocumentType.MEETING_MINUTES,
                style=TemplateStyle.MODERN,
                css_styles=styles[TemplateStyle.MODERN.value],
                template_html=self._get_meeting_modern_template(),
                variables=['meeting_title', 'meeting_date', 'attendees', 'agenda_items', 'discussion_points', 'action_items', 'next_meeting_date', 'meeting_organizer'],
                category="会議・ミーティング",
                tags=["モダン", "カラフル", "視覚的"]
            ),
            JapaneseTemplate(
                id="meeting_minimal_ja",
                name="会議議事録（ミニマル）",
                description="シンプルで読みやすいミニマルデザイン",
                document_type=DocumentType.MEETING_MINUTES,
                style=TemplateStyle.MINIMAL,
                css_styles=styles[TemplateStyle.MINIMAL.value],
                template_html=self._get_meeting_minimal_template(),
                variables=['meeting_title', 'meeting_date', 'attendees', 'agenda_items', 'discussion_points', 'action_items'],
                category="会議・ミーティング",
                tags=["ミニマル", "シンプル", "読みやすい"]
            )
        ])
        
        # Letter Templates
        templates.extend([
            JapaneseTemplate(
                id="letter_formal_ja",
                name="正式な手紙（フォーマル）",
                description="正式なビジネス文書に適したクラシックなデザイン",
                document_type=DocumentType.LETTER,
                style=TemplateStyle.FORMAL,
                css_styles=styles[TemplateStyle.FORMAL.value],
                template_html=self._get_letter_formal_template(),
                variables=['sender_name', 'sender_title', 'sender_company', 'recipient_name', 'recipient_title', 'recipient_company', 'date', 'subject', 'body'],
                category="手紙・文書",
                tags=["フォーマル", "ビジネス", "正式"]
            ),
            JapaneseTemplate(
                id="letter_modern_ja",
                name="ビジネスレター（モダン）",
                description="現代的なビジネスレターのデザイン",
                document_type=DocumentType.LETTER,
                style=TemplateStyle.MODERN,
                css_styles=styles[TemplateStyle.MODERN.value],
                template_html=self._get_letter_modern_template(),
                variables=['sender_name', 'sender_company', 'recipient_name', 'recipient_company', 'date', 'subject', 'body'],
                category="手紙・文書",
                tags=["モダン", "ビジネス", "現代的"]
            )
        ])
        
        # Report Templates
        templates.extend([
            JapaneseTemplate(
                id="report_professional_ja",
                name="ビジネスレポート（プロフェッショナル）",
                description="詳細なビジネスレポートに適したデザイン",
                document_type=DocumentType.REPORT,
                style=TemplateStyle.PROFESSIONAL,
                css_styles=styles[TemplateStyle.PROFESSIONAL.value],
                template_html=self._get_report_professional_template(),
                variables=['report_title', 'author', 'date', 'summary', 'content_sections', 'conclusions', 'recommendations'],
                category="レポート・報告書",
                tags=["ビジネス", "分析", "プロフェッショナル"]
            ),
            JapaneseTemplate(
                id="report_creative_ja",
                name="クリエイティブレポート",
                description="クリエイティブで印象的なレポートデザイン",
                document_type=DocumentType.REPORT,
                style=TemplateStyle.CREATIVE,
                css_styles=styles[TemplateStyle.CREATIVE.value],
                template_html=self._get_report_creative_template(),
                variables=['report_title', 'author', 'date', 'summary', 'content_sections', 'key_insights'],
                category="レポート・報告書",
                tags=["クリエイティブ", "印象的", "カラフル"]
            )
        ])
        
        # Flyer Templates
        templates.extend([
            JapaneseTemplate(
                id="flyer_event_ja",
                name="イベントフライヤー",
                description="イベント告知に最適なデザイン",
                document_type=DocumentType.FLYER,
                style=TemplateStyle.MODERN,
                css_styles=styles[TemplateStyle.MODERN.value],
                template_html=self._get_flyer_event_template(),
                variables=['headline', 'event_name', 'event_date', 'event_time', 'location', 'description', 'contact_info', 'call_to_action'],
                category="フライヤー・チラシ",
                tags=["イベント", "告知", "カラフル"]
            ),
            JapaneseTemplate(
                id="flyer_business_ja",
                name="ビジネスフライヤー",
                description="ビジネス向けのプロフェッショナルなフライヤー",
                document_type=DocumentType.FLYER,
                style=TemplateStyle.PROFESSIONAL,
                css_styles=styles[TemplateStyle.PROFESSIONAL.value],
                template_html=self._get_flyer_business_template(),
                variables=['company_name', 'service_title', 'service_description', 'benefits', 'contact_info', 'call_to_action'],
                category="フライヤー・チラシ",
                tags=["ビジネス", "サービス", "プロフェッショナル"]
            )
        ])
        
        return templates
    
    def get_templates_by_type(self, document_type: DocumentType) -> List[JapaneseTemplate]:
        """Get templates by document type"""
        return [t for t in self.templates if t.document_type == document_type]
    
    def get_template_by_id(self, template_id: str) -> JapaneseTemplate:
        """Get template by ID"""
        for template in self.templates:
            if template.id == template_id:
                return template
        raise ValueError(f"Template with ID {template_id} not found")
    
    def get_templates_by_style(self, style: TemplateStyle) -> List[JapaneseTemplate]:
        """Get templates by style"""
        return [t for t in self.templates if t.style == style]
    
    def _get_meeting_professional_template(self) -> str:
        return '''
        <div class="date-header">{{ format_date(meeting_date, "%Y年%m月%d日") }}</div>
        
        <h1>{{ meeting_title }}</h1>
        
        <div class="card">
            <h2>📋 会議概要</h2>
            <p><strong>主催者：</strong>{{ meeting_organizer }}</p>
            <p><strong>出席者：</strong>
            {% for attendee in attendees %}
                {{ attendee }}{% if not loop.last %}, {% endif %}
            {% endfor %}
            </p>
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
        {% for action in action_items %}
        <div class="card">
            <strong>{{ action.task }}</strong><br>
            担当者: {{ action.owner }}<br>
            期限: {{ format_date(action.due_date, "%m月%d日") if action.due_date else "未定" }}
        </div>
        {% endfor %}
        
        <div class="footer">
            次回会議: {{ format_date(next_meeting_date, "%Y年%m月%d日") if next_meeting_date else "未定" }}
        </div>
        '''
    
    def _get_meeting_modern_template(self) -> str:
        return '''
        <div class="badge">{{ format_date(meeting_date, "%Y年%m月%d日") }}</div>
        
        <h1>{{ meeting_title }}</h1>
        
        <div class="card">
            <h2><span class="emoji-header">📋</span>会議概要</h2>
            <p><strong>主催者：</strong>{{ meeting_organizer }}</p>
            <div style="margin-top: 16px;">
            {% for attendee in attendees %}
                <span class="tag">{{ attendee }}</span>
            {% endfor %}
            </div>
        </div>
        
        <h2><span class="emoji-header">📝</span>議題</h2>
        <div class="card">
            <ol>
            {% for item in agenda_items %}
                <li>{{ item }}</li>
            {% endfor %}
            </ol>
        </div>
        
        <h2><span class="emoji-header">💬</span>討議内容</h2>
        <div class="card">
            {{ discussion_points | markdown }}
        </div>
        
        <h2><span class="emoji-header">✅</span>アクション項目</h2>
        {% for action in action_items %}
        <div class="card" style="border-left: 4px solid #3b82f6;">
            <strong>{{ action.task }}</strong><br>
            担当者: {{ action.owner }}<br>
            期限: {{ format_date(action.due_date, "%m月%d日") if action.due_date else "未定" }}
        </div>
        {% endfor %}
        '''
    
    def _get_meeting_minimal_template(self) -> str:
        return '''
        <div class="date-simple">{{ format_date(meeting_date, "%Y年%m月%d日") }}</div>
        
        <h1>{{ meeting_title }}</h1>
        
        <hr class="minimal-divider">
        
        <h2>出席者</h2>
        <p>
        {% for attendee in attendees %}
            {{ attendee }}{% if not loop.last %}, {% endif %}
        {% endfor %}
        </p>
        
        <h2>議題</h2>
        {% for item in agenda_items %}
        <p>{{ loop.index }}. {{ item }}</p>
        {% endfor %}
        
        <h2>討議内容</h2>
        {{ discussion_points | markdown }}
        
        <h2>アクション項目</h2>
        {% for action in action_items %}
        <div class="minimal-highlight">
            {{ action.task }} ({{ action.owner }})
        </div>
        {% endfor %}
        '''
    
    def _get_letter_formal_template(self) -> str:
        return '''
        <div class="date-line">{{ format_date(date, "%Y年%m月%d日") }}</div>
        
        <div class="formal-box">
            {{ recipient_company }}<br>
            {{ recipient_title }} {{ recipient_name }} 様
        </div>
        
        <h1>{{ subject }}</h1>
        
        <p>拝啓　時下ますますご清栄のこととお慶び申し上げます。</p>
        
        {{ body | markdown }}
        
        <p>何かご不明な点がございましたら、お気軽にお問い合わせください。</p>
        <p>今後ともよろしくお願い申し上げます。</p>
        
        <div class="signature-section">
            <p>敬具</p>
            <div style="margin-top: 40px;">
                {{ sender_company }}<br>
                {{ sender_title }}<br>
                <strong>{{ sender_name }}</strong>
            </div>
        </div>
        '''
    
    def _get_letter_modern_template(self) -> str:
        return '''
        <div class="badge">{{ format_date(date, "%Y年%m月%d日") }}</div>
        
        <div class="card">
            <strong>宛先:</strong> {{ recipient_company }} {{ recipient_name }} 様
        </div>
        
        <h1>{{ subject }}</h1>
        
        <div class="card">
            {{ body | markdown }}
        </div>
        
        <div class="card" style="text-align: right;">
            <strong>{{ sender_company }}</strong><br>
            {{ sender_name }}
        </div>
        '''
    
    def _get_report_professional_template(self) -> str:
        return '''
        <div class="date-header">{{ format_date(date, "%Y年%m月%d日") }}</div>
        
        <h1>{{ report_title }}</h1>
        
        <div class="card">
            <h2>📊 概要</h2>
            <p><strong>作成者：</strong>{{ author }}</p>
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
        '''
    
    def _get_report_creative_template(self) -> str:
        return '''
        <div class="content">
            <div class="badge">{{ format_date(date, "%Y年%m月%d日") }}</div>
            
            <h1>{{ report_title }}</h1>
            
            <div class="creative-card">
                <h2><span class="emoji-header">📊</span>概要</h2>
                <p><strong>作成者：</strong>{{ author }}</p>
                {{ summary | markdown }}
            </div>
            
            {% for section in content_sections %}
            <div class="creative-card">
                <h2><span class="emoji-header">📋</span>{{ section.title }}</h2>
                {{ section.content | markdown }}
            </div>
            {% endfor %}
            
            <div class="creative-card">
                <h2><span class="emoji-header">💡</span>重要なインサイト</h2>
                {% for insight in key_insights %}
                <div class="highlight">{{ insight }}</div>
                {% endfor %}
            </div>
        </div>
        '''
    
    def _get_flyer_event_template(self) -> str:
        return '''
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
        
        <div class="card" style="background: #dcfce7; border-left-color: #22c55e; text-align: center;">
            <h3 style="color: #15803d;">{{ call_to_action }}</h3>
            <p><strong>お問い合わせ：</strong>{{ contact_info }}</p>
        </div>
        '''
    
    def _get_flyer_business_template(self) -> str:
        return '''
        <h1 style="text-align: center;">{{ company_name }}</h1>
        
        <div class="card" style="text-align: center;">
            <h2>{{ service_title }}</h2>
            {{ service_description | markdown }}
        </div>
        
        <h2>✨ サービスの特徴</h2>
        {% for benefit in benefits %}
        <div class="card">
            <span class="highlight">{{ benefit }}</span>
        </div>
        {% endfor %}
        
        <div class="card" style="background: #f0f9ff; border-left-color: #0ea5e9; text-align: center;">
            <h3>{{ call_to_action }}</h3>
            <p><strong>お問い合わせ：</strong>{{ contact_info }}</p>
        </div>
        
        <div class="footer">
            {{ company_name }} - プロフェッショナルなサービスをお届けします
        </div>
        '''