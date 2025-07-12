"""
PDF Generation Service
Converts HTML/CSS content to PDF using ReportLab
"""
import tempfile
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import html2text
from bs4 import BeautifulSoup

from ..config import settings
from ..models.audio import PDFGenerationRequest, PDFGenerationResponse

logger = logging.getLogger(__name__)

class PDFService:
    """Service for PDF generation from HTML/CSS content"""
    
    def __init__(self):
        self.output_dir = Path(settings.PDF_OUTPUT_DIR)
        self.output_dir.mkdir(exist_ok=True)
        
        # Register Japanese fonts
        self._register_japanese_fonts()
        
        # Set up default styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _register_japanese_fonts(self):
        """Register Japanese fonts for PDF generation"""
        try:
            # Try to use system fonts first
            import subprocess
            import platform
            
            if platform.system() == "Darwin":  # macOS
                # Try common Japanese fonts on macOS
                font_paths = [
                    "/System/Library/Fonts/ヒラギノ角ゴシック W3.otf",
                    "/System/Library/Fonts/Hiragino Sans GB.ttc",
                    "/Library/Fonts/Arial Unicode MS.ttf",
                ]
            elif platform.system() == "Linux":  # Linux/Docker
                font_paths = [
                    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
                    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
                    "/usr/share/fonts/opentype/ipafont-mincho/ipam.ttf",
                    "/usr/share/fonts/opentype/ipafont-mincho/ipamp.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                ]
            else:  # Windows
                font_paths = [
                    "C:/Windows/Fonts/msgothic.ttc",
                    "C:/Windows/Fonts/msmincho.ttc",
                ]
            
            # Try to register the first available font
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('Japanese', font_path))
                        logger.info(f"Successfully registered Japanese font: {font_path}")
                        return
                    except Exception as e:
                        logger.warning(f"Failed to register font {font_path}: {e}")
                        continue
            
            # Fallback: Use built-in fonts that support some Unicode
            logger.warning("No Japanese fonts found, falling back to Helvetica")
            
        except Exception as e:
            logger.error(f"Error setting up Japanese fonts: {e}")
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles for documents"""
        
        # Get font name - use Japanese if available, otherwise fallback
        font_name = 'Japanese' if 'Japanese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        
        # Title style for flyers/announcements
        self.styles.add(ParagraphStyle(
            name='FlyerTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2C3E50'),
            fontName=font_name
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='FlyerSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#34495E'),
            fontName=font_name
        ))
        
        # Body text for announcements
        self.styles.add(ParagraphStyle(
            name='AnnouncementBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20,
            fontName=font_name
        ))
        
        # Event details style
        self.styles.add(ParagraphStyle(
            name='EventDetails',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=10,
            alignment=TA_LEFT,
            leftIndent=30,
            bulletIndent=20,
            fontName=font_name
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=HexColor('#7F8C8D'),
            fontName=font_name
        ))
    
    async def generate_pdf(
        self,
        html_content: str,
        css_content: str,
        title: str
    ) -> Dict[str, Any]:
        """
        Generate PDF from HTML/CSS content
        
        Args:
            request: PDF generation request with HTML/CSS content
            
        Returns:
            PDF generation response with file path and metadata
        """
        try:
            # Create unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = self._sanitize_filename(title)
            filename = f"{safe_title}_{timestamp}.pdf"
            file_path = self.output_dir / filename
            
            logger.info(f"Generating PDF: {filename}")
            
            # Parse HTML content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(file_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            story = await self._build_pdf_content(soup, "flyer", story)
            
            # Generate PDF
            doc.build(story)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            logger.info(f"PDF generated successfully: {filename} ({file_size} bytes)")
            
            return {
                "success": True,
                "file_path": str(file_path),
                "filename": filename,
                "file_size": file_size
            }
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return {
                "success": False,
                "file_path": None,
                "filename": "",
                "file_size": 0
            }
    
    async def _build_pdf_content(
        self, 
        soup: BeautifulSoup, 
        document_type: str, 
        story: list
    ) -> list:
        """
        Build PDF content from parsed HTML
        
        Args:
            soup: Parsed HTML content
            document_type: Type of document being generated
            story: ReportLab story list to append content to
            
        Returns:
            Updated story list with PDF content
        """
        # Get font name - use Japanese if available, otherwise fallback
        font_name = 'Japanese' if 'Japanese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        
        # Process document in DOM order to maintain structure
        def process_element(element):
            """Process a single element and add to story"""
            if element.name == 'h1':
                # Main title
                text = element.get_text().strip()
                if text:
                    story.append(Paragraph(text, self.styles['FlyerTitle']))
                    story.append(Spacer(1, 0.3*inch))
                    
            elif element.name == 'h2':
                # Section headers
                text = element.get_text().strip()
                if text:
                    heading_style = ParagraphStyle(
                        name='SectionHeading',
                        fontSize=16,
                        spaceAfter=8,
                        spaceBefore=12,
                        textColor=HexColor('#007BFF'),
                        fontName=font_name,
                        alignment=TA_LEFT
                    )
                    story.append(Paragraph(text, heading_style))
                    
            elif element.name == 'h3':
                # Subsection headers
                text = element.get_text().strip()
                if text:
                    heading_style = ParagraphStyle(
                        name='SubsectionHeading',
                        fontSize=14,
                        spaceAfter=6,
                        spaceBefore=10,
                        textColor=HexColor('#333333'),
                        fontName=font_name,
                        alignment=TA_LEFT
                    )
                    story.append(Paragraph(text, heading_style))
                    
            elif element.name == 'p':
                # Paragraphs
                text = element.get_text().strip()
                if text:
                    # Check if this is a subtitle (first p after h1)
                    prev_sibling = element.find_previous_sibling()
                    if prev_sibling and prev_sibling.name == 'h1':
                        # This is a subtitle
                        story.append(Paragraph(text, self.styles['FlyerSubtitle']))
                        story.append(Spacer(1, 0.2*inch))
                    else:
                        # Regular paragraph
                        para_style = ParagraphStyle(
                            name='BodyParagraph',
                            fontSize=12,
                            spaceAfter=8,
                            spaceBefore=4,
                            leftIndent=0,
                            rightIndent=0,
                            alignment=TA_JUSTIFY,
                            lineHeight=1.5,
                            fontName=font_name
                        )
                        story.append(Paragraph(text, para_style))
                        
            elif element.name == 'ul':
                # Unordered lists
                for li in element.find_all('li', recursive=False):
                    text = li.get_text().strip()
                    if text:
                        bullet_style = ParagraphStyle(
                            name='BulletPoint',
                            fontSize=12,
                            spaceAfter=4,
                            leftIndent=20,
                            bulletIndent=10,
                            fontName=font_name
                        )
                        story.append(Paragraph(f"• {text}", bullet_style))
                        
            elif element.name == 'ol':
                # Ordered lists
                for i, li in enumerate(element.find_all('li', recursive=False), 1):
                    text = li.get_text().strip()
                    if text:
                        number_style = ParagraphStyle(
                            name='NumberedPoint',
                            fontSize=12,
                            spaceAfter=4,
                            leftIndent=20,
                            bulletIndent=10,
                            fontName=font_name
                        )
                        story.append(Paragraph(f"{i}. {text}", number_style))
        
        # Find the main document container
        document_container = soup.find(['div', 'article', 'main'], class_=['document', 'content']) or soup
        
        # Process all elements in DOM order
        for element in document_container.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'ul', 'ol'], recursive=True):
            # Skip if element is inside a nested container we'll process separately
            parent_containers = element.find_parents(['header', 'footer', 'nav', 'aside'])
            if not parent_containers:
                process_element(element)
        
        # Process header section if present
        header = soup.find('header')
        if header:
            # Header is usually processed above, but handle special cases
            pass
            
        # Process footer section if present
        footer = soup.find('footer')
        if footer:
            story.append(Spacer(1, 0.3*inch))
            
            for element in footer.find_all(['h1', 'h2', 'h3', 'h4', 'p'], recursive=True):
                if element.name in ['h1', 'h2', 'h3']:
                    text = element.get_text().strip()
                    if text:
                        footer_heading_style = ParagraphStyle(
                            name='FooterHeading',
                            fontSize=16,
                            spaceAfter=8,
                            alignment=TA_CENTER,
                            textColor=HexColor('#333333'),
                            fontName=font_name
                        )
                        story.append(Paragraph(text, footer_heading_style))
                elif element.name == 'p':
                    text = element.get_text().strip()
                    if text:
                        footer_para_style = ParagraphStyle(
                            name='FooterParagraph',
                            fontSize=12,
                            spaceAfter=8,
                            alignment=TA_CENTER,
                            fontName=font_name
                        )
                        story.append(Paragraph(text, footer_para_style))
        
        # Add footer space
        story.append(Spacer(1, 0.5*inch))
        
        # Add generated timestamp
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        footer_text = f"Generated by AI Printer on {timestamp}"
        story.append(Paragraph(footer_text, self.styles['ContactInfo']))
        
        return story
    
    def _sanitize_filename(self, title: str) -> str:
        """
        Sanitize document title for use as filename
        
        Args:
            title: Document title
            
        Returns:
            Sanitized filename string
        """
        # Remove special characters and replace spaces
        import re
        sanitized = re.sub(r'[^\w\s-]', '', title)
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        sanitized = sanitized.strip('_')
        
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        
        return sanitized or "document"
    
    async def create_flyer_from_template(
        self,
        title: str,
        content: str,
        event_details: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create a flyer using a predefined template
        
        Args:
            title: Flyer title
            content: Main content text
            event_details: Optional event details (date, time, location, etc.)
            
        Returns:
            Path to generated PDF file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = self._sanitize_filename(title)
        filename = f"flyer_{safe_title}_{timestamp}.pdf"
        file_path = self.output_dir / filename
        
        doc = SimpleDocTemplate(
            str(file_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Add title
        story.append(Paragraph(title, self.styles['FlyerTitle']))
        story.append(Spacer(1, 0.4*inch))
        
        # Add main content
        story.append(Paragraph(content, self.styles['AnnouncementBody']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add event details if provided
        if event_details:
            story.append(Paragraph("Event Details:", self.styles['Heading3']))
            story.append(Spacer(1, 0.1*inch))
            
            for key, value in event_details.items():
                detail_text = f"<b>{key.title()}:</b> {value}"
                story.append(Paragraph(detail_text, self.styles['EventDetails']))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"Flyer template generated: {filename}")
        return str(file_path)
    
    async def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old PDF files to save disk space
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
        """
        try:
            current_time = datetime.now().timestamp()
            max_age_seconds = max_age_hours * 3600
            
            deleted_count = 0
            for file_path in self.output_dir.glob("*.pdf"):
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old PDF files")
                
        except Exception as e:
            logger.warning(f"PDF cleanup failed: {e}")

# Global service instance
pdf_service = PDFService()

def get_pdf_service() -> PDFService:
    """Get PDF service instance"""
    return pdf_service
