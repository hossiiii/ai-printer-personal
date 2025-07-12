## FEATURE:

Build an AI Printer system - a voice-to-document application for creating flyers and announcements. Users record brief voice instructions (1-2 sentences), and the system uses AI to generate professionally formatted PDF documents.

The system should include:
- Web-based voice recording interface for brief instructions
- Speech recognition using OpenAI Whisper API (WAV format only)
- LLM-powered document generation using OpenAI GPT API to determine content and template
- PDF preview system for user review before final generation
- Voice-based revision system - users can record additional instructions to modify the document
- Automatic PDF creation with professional layouts using reportlab
- Google Drive integration with organized folder structure: /AI-Printer/[Year]/[Month]/[Document-Type]/
- Simple document generation (no user management)
- Mobile-responsive design for voice recording on any device

Technical Requirements:
- **Backend**: FastAPI with Python 3.11+, async/await throughout
- **Frontend**: React with TypeScript, Web Audio API for recording (WAV format)
- **Storage**: Google Drive API v3 with OAuth2 for user-specific storage
- **Authentication**: Google OAuth2 for Drive access only
- **Transcription**: OpenAI Whisper API
- **Document Generation**: reportlab for PDF creation only
- **LLM Integration**: OpenAI GPT API for content generation and template selection
- **Preview System**: HTML/CSS preview before PDF generation
- **Revision System**: Support multiple voice inputs for document refinement
- **Audio Processing**: No persistent audio storage - process and discard
- **Development Environment**: Docker & Docker Compose for local development
- **Development Mode**: Mock storage for local development, Google Drive for production

The workflow should be:

**Initial Document Creation:**
1. User clicks "Start Recording" and speaks brief instructions (1-2 sentences)
2. Real-time audio visualization shows recording progress (WAV format)
3. User stops recording, audio uploads to backend
4. Backend converts speech to text using OpenAI Whisper API
5. Audio file is immediately discarded after transcription
6. OpenAI GPT API analyzes the instruction and determines:
   - Document type (flyer, announcement, notice, etc.)
   - Content structure and layout
   - Appropriate template selection
7. System generates HTML/CSS preview of the document
8. User reviews the preview on screen

**Revision Process (if needed):**
9. If user wants changes, they click "Record Revision" 
10. User speaks revision instructions ("make the title bigger", "change the date", "add contact info")
11. System processes revision voice input
12. GPT API applies the changes to the document
13. Updated preview is displayed
14. Steps 9-13 repeat until user is satisfied

**Final Generation:**
15. User clicks "Generate PDF"
16. reportlab converts the final design to PDF
17. Document saves to /AI-Printer/[Year]/[Month]/[Document-Type]/ in Google Drive (prod) or local folder (dev)
18. User receives download link (dev) or shareable Drive link (prod)

## DEVELOPMENT SETUP:

The system should be fully containerized for local development:

**Docker Compose Services:**
- **backend**: FastAPI server with hot reload
- **frontend**: React development server with hot reload

**Local URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

**Environment Variables Setup:**
```bash
# .env.development
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
DEVELOPMENT=true
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# .env.production
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
DEVELOPMENT=false
FRONTEND_URL=https://your-domain.com
BACKEND_URL=https://api.your-domain.com
```

**Development Commands:**
```bash
# Start all services
docker-compose up

# Start with rebuild
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Stop all services
docker-compose down

# Run tests
docker-compose exec backend pytest
```
## EXAMPLES:

See examples/README.md for code patterns including:
- Voice upload endpoint with WAV file validation
- Google Drive integration with /AI-Printer/[Year]/[Month]/[Document-Type]/ folder organization  
- Document generation with Flyer, Announcement, Notice, Event templates
- HTML/CSS preview generation for document layouts
- Voice-based revision processing and document updates
- Frontend voice recording component patterns (WAV format)

## DOCUMENTATION - Research these APIs thoroughly before implementation:

OpenAI API Documentation: https://platform.openai.com/docs/overview
Google Drive API v3: https://developers.google.com/drive/api/v3/about-sdk
Google OAuth2 Setup: https://developers.google.com/identity/protocols/oauth2
FastAPI Documentation: https://fastapi.tiangolo.com/
Web Audio API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
React Documentation: https://react.dev/
ReportLab Documentation: https://www.reportlab.com/docs/reportlab-userguide.pdf

## OTHER CONSIDERATIONS:
- **Docker Configuration**: Multi-stage builds for production optimization
- **Environment Variables**: Separate .env files for development and production
- **Mock Mode**: DEVELOPMENT=true for local file storage, false for Google Drive
- **Audio Processing**: WAV format only, immediate deletion after transcription
- **Document Templates**: Flyer, Announcement, Notice, Event templates with professional layouts
- **Preview System**: Real-time HTML/CSS preview with responsive design
- **Revision Workflow**: Multi-step voice-based document refinement process
- **Volume Mounting**: Source code mounting for development hot reload
- **Network Configuration**: Internal Docker network for service communication
- **Health Checks**: Container health monitoring and automatic restart
- **Security**: Validate WAV uploads, implement rate limiting, secure API key management
- **Accessibility**: Ensure keyboard navigation, screen reader support
- **Mobile**: Touch-friendly recording interface, responsive design
- **Error Handling**: Graceful fallbacks for transcription failures, network issues
- **Privacy**: No audio storage, immediate deletion after processing
- **Scalability**: Containerized deployment, load balancing ready
- **Monitoring**: Comprehensive logging, error tracking, usage analytics

Designsystem.md - must be adhered to at all times for building any new features