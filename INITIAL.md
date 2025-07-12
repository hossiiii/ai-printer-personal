## FEATURE:

Build an AI Printer system - a voice-to-document application that allows users to record voice, converts speech to text, then uses LLM to automatically generate structured documents and save as PDF to Google Drive.

The system should include:
- Web-based voice recording interface with real-time visualization
- Speech recognition using OpenAI Whisper API
- LLM-powered document generation using GPT-4 or Claude for intelligent formatting
- Automatic PDF creation with professional layouts
- Google Drive integration with organized folder structure
- User authentication and document management
- Mobile-responsive design for voice recording on any device

Technical Requirements:
- **Backend**: FastAPI with Python 3.11+, async/await throughout
- **Frontend**: React with TypeScript, Web Audio API for recording
- **Storage**: Google Drive API v3 for document storage
- **Authentication**: JWT tokens with Google OAuth2 integration
- **Transcription**: OpenAI Whisper API
- **Document Generation**: python-docx for DOCX, reportlab for PDF
- **Real-time Features**: WebSocket for live transcription feedback
- **Development Environment**: Docker & Docker Compose for local development
- **Database**: PostgreSQL for user data and document metadata
- **Cache**: Redis for session and transcription caching
The workflow should be:
1. User clicks "Start Recording" in browser
2. Real-time audio visualization shows recording progress  
3. User stops recording, audio uploads to backend
4. Backend converts speech to text using OpenAI Whisper API
5. User can edit transcription before document generation
6. User selects document template and generates formatted document
7. Document automatically saves to organized Google Drive folder
8. User receives shareable link and download options

## DEVELOPMENT SETUP:

The system should be fully containerized for local development:

**Docker Compose Services:**
- **backend**: FastAPI server with hot reload
- **frontend**: React development server with hot reload
- **postgres**: PostgreSQL database for user data
- **redis**: Redis for caching and session storage

**Local URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

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
```
## EXAMPLES:

See examples/README.md for code patterns including:
- Voice upload endpoint with file validation
- Google Drive integration with folder organization  
- Document generation with multiple templates
- Frontend voice recording component patterns

## DOCUMENTATION - Research these APIs thoroughly before implementation:

OpenAI API Documentation: https://platform.openai.com/docs/overview
Google Drive API v3: https://developers.google.com/drive/api/v3/about-sdk

FastAPI Documentation: https://fastapi.tiangolo.com/
Web Audio API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API
Google OAuth2: https://developers.google.com/identity/protocols/oauth2
React Documentation: https://react.dev/
python-docx Documentation: https://python-docx.readthedocs.io/
WebSocket with FastAPI: https://fastapi.tiangolo.com/advanced/websockets/

## OTHER CONSIDERATIONS:
- **Docker Configuration**: Multi-stage builds for production optimization
- **Environment Variables**: Separate .env files for development and production
- **Volume Mounting**: Source code mounting for development hot reload
- **Network Configuration**: Internal Docker network for service communication
- **Health Checks**: Container health monitoring and automatic restart
- **Security**: Validate all audio uploads, implement rate limiting, secure credential storage
- **Performance**: Use Redis for caching, implement background job processing
- **Accessibility**: Ensure keyboard navigation, screen reader support
- **Mobile**: Touch-friendly recording interface, responsive design
- **Error Handling**: Graceful fallbacks for transcription failures, network issues
- **Privacy**: Clear data retention policy, GDPR compliance options
- **Scalability**: Containerized deployment, load balancing ready
- **Monitoring**: Comprehensive logging, error tracking, usage analytics

Designsystem.md - must be adhered to at all times for building any new features