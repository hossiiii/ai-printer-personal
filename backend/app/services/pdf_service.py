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
        
        # Set up default styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles for documents"""
        
        # Title style for flyers/announcements
        self.styles.add(ParagraphStyle(
            name='FlyerTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2C3E50')
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='FlyerSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#34495E')
        ))
        
        # Body text for announcements
        self.styles.add(ParagraphStyle(
            name='AnnouncementBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20
        ))
        
        # Event details style
        self.styles.add(ParagraphStyle(
            name='EventDetails',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=10,
            alignment=TA_LEFT,
            leftIndent=30,
            bulletIndent=20
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=HexColor('#7F8C8D')
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
        # Add document title
        title_elem = soup.find(['h1', 'title'])
        if title_elem:
            title_text = title_elem.get_text().strip()
            story.append(Paragraph(title_text, self.styles['FlyerTitle']))
            story.append(Spacer(1, 0.3*inch))
        
        # Add subtitle if present
        subtitle_elem = soup.find('h2')
        if subtitle_elem:
            subtitle_text = subtitle_elem.get_text().strip()
            story.append(Paragraph(subtitle_text, self.styles['FlyerSubtitle']))
            story.append(Spacer(1, 0.2*inch))
        
        # Process main content
        content_elements = soup.find_all(['p', 'div', 'h3', 'h4', 'ul', 'ol'])
        
        for elem in content_elements:
            if elem.name in ['h3', 'h4']:
                # Section headers
                text = elem.get_text().strip()
                if text:
                    story.append(Paragraph(text, self.styles['Heading3']))
                    story.append(Spacer(1, 0.1*inch))
                    
            elif elem.name == 'p':
                # Paragraphs
                text = elem.get_text().strip()
                if text:
                    # Choose style based on document type
                    if document_type in ['announcement', 'notice']:
                        style = self.styles['AnnouncementBody']
                    else:
                        style = self.styles['Normal']
                    
                    story.append(Paragraph(text, style))
                    story.append(Spacer(1, 0.1*inch))
                    
            elif elem.name in ['ul', 'ol']:
                # Lists
                for li in elem.find_all('li'):
                    text = li.get_text().strip()
                    if text:
                        bullet_text = f"• {text}" if elem.name == 'ul' else f"1. {text}"
                        story.append(Paragraph(bullet_text, self.styles['EventDetails']))
                        
            elif elem.name == 'div':
                # Generic content divs
                text = elem.get_text().strip()
                if text and len(text) > 10:  # Avoid empty or very short divs
                    # Check for contact info patterns
                    if any(keyword in text.lower() for keyword in ['contact', 'phone', 'email', 'address']):
                        story.append(Paragraph(text, self.styles['ContactInfo']))
                    else:
                        story.append(Paragraph(text, self.styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
        
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
