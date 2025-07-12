"""
Google Drive Service Integration
Handles OAuth2 authentication and file storage with organized folder structure
"""
import asyncio
import os
import tempfile
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import aiofiles

from ..config import settings

logger = logging.getLogger(__name__)

class DriveService:
    """Service for Google Drive API integration"""
    
    def __init__(self):
        if not settings.DEVELOPMENT and (not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET):
            raise ValueError("Google Drive credentials not configured")
        
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.scopes = ['https://www.googleapis.com/auth/drive.file']
        
        # Drive folder structure: /AI-Printer/[Year]/[Month]/[Document-Type]/
        self.base_folder_name = "AI-Printer"
        
    def get_auth_url(self, state: Optional[str] = None) -> str:
        """
        Generate OAuth2 authorization URL
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL for user to authenticate
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state
        )
        
        logger.info(f"Generated auth URL for Drive access")
        return auth_url
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access tokens
        
        Args:
            code: Authorization code from OAuth callback
            
        Returns:
            Dictionary containing access and refresh tokens
        """
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            # Exchange code for tokens
            flow.fetch_token(code=code)
            
            credentials = flow.credentials
            
            logger.info("Successfully exchanged authorization code for tokens")
            
            return {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes
            }
            
        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            raise Exception(f"Failed to exchange authorization code: {str(e)}")
    
    async def upload_pdf(
        self,
        file_path: str,
        filename: str,
        document_type: str
    ) -> str:
        """
        Upload PDF file to Google Drive with organized folder structure
        
        Args:
            file_path: Local path to PDF file
            filename: Desired filename in Drive
            document_type: Type of document for folder organization
            access_token: User's access token
            refresh_token: User's refresh token for token refresh
            
        Returns:
            Dictionary with file info and Drive link
        """
        try:
            # For development mode, return a mock Drive link
            if settings.DEVELOPMENT:
                logger.info(f"Development mode: skipping actual Drive upload for {filename}")
                return f"https://drive.google.com/file/d/mock_file_id/view"
            
            # TODO: Implement production Drive upload with proper OAuth flow
            # This would require user authentication flow
            logger.warning("Production Drive upload not yet implemented")
            return f"https://drive.google.com/file/d/placeholder_id/view"
            
        except Exception as e:
            logger.error(f"Drive upload failed: {e}")
            raise Exception(f"Failed to upload to Google Drive: {str(e)}")
    
    async def _ensure_folder_structure(self, service, document_type: str) -> str:
        """
        Ensure proper folder structure exists in Drive
        Structure: /AI-Printer/[Year]/[Month]/[Document-Type]/
        
        Args:
            service: Google Drive API service
            document_type: Type of document for final folder
            
        Returns:
            Folder ID for the document type folder
        """
        now = datetime.now()
        year = str(now.year)
        month = f"{now.month:02d}-{now.strftime('%B')}"
        
        # Find or create base folder (AI-Printer)
        base_folder_id = await self._find_or_create_folder(
            service, self.base_folder_name, None
        )
        
        # Find or create year folder
        year_folder_id = await self._find_or_create_folder(
            service, year, base_folder_id
        )
        
        # Find or create month folder
        month_folder_id = await self._find_or_create_folder(
            service, month, year_folder_id
        )
        
        # Find or create document type folder
        doc_type_folder_id = await self._find_or_create_folder(
            service, document_type.title(), month_folder_id
        )
        
        logger.info(f"Ensured folder structure: {self.base_folder_name}/{year}/{month}/{document_type.title()}")
        
        return doc_type_folder_id
    
    async def _find_or_create_folder(
        self, 
        service, 
        folder_name: str, 
        parent_id: Optional[str]
    ) -> str:
        """
        Find existing folder or create new one
        
        Args:
            service: Google Drive API service
            folder_name: Name of folder to find/create
            parent_id: Parent folder ID (None for root)
            
        Returns:
            Folder ID
        """
        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            # Folder exists, return its ID
            return folders[0]['id']
        
        # Create new folder
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            folder_metadata['parents'] = [parent_id]
        
        folder = service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        
        logger.info(f"Created Drive folder: {folder_name}")
        
        return folder.get('id')
    
    async def _get_folder_path(self, document_type: str) -> str:
        """
        Get the full folder path for organization
        
        Args:
            document_type: Type of document
            
        Returns:
            Full folder path string
        """
        now = datetime.now()
        year = str(now.year)
        month = f"{now.month:02d}-{now.strftime('%B')}"
        
        return f"{self.base_folder_name}/{year}/{month}/{document_type.title()}"
    
    async def list_user_files(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List recent files in AI-Printer folder
        
        Args:
            access_token: User's access token
            refresh_token: User's refresh token
            limit: Maximum number of files to return
            
        Returns:
            List of file information dictionaries
        """
        try:
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            if credentials.expired:
                credentials.refresh(Request())
            
            service = build('drive', 'v3', credentials=credentials)
            
            # Find base folder
            base_query = f"name='{self.base_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            base_results = service.files().list(q=base_query, fields='files(id)').execute()
            
            if not base_results.get('files'):
                return []
            
            base_folder_id = base_results['files'][0]['id']
            
            # List files in AI-Printer folder tree
            files_query = f"'{base_folder_id}' in parents or parents in (select id from files where '{base_folder_id}' in parents)"
            files_results = service.files().list(
                q=files_query,
                orderBy='createdTime desc',
                pageSize=limit,
                fields='files(id,name,webViewLink,createdTime,size,mimeType)'
            ).execute()
            
            files = []
            for file_info in files_results.get('files', []):
                if file_info.get('mimeType') == 'application/pdf':
                    files.append({
                        "file_id": file_info.get('id'),
                        "filename": file_info.get('name'),
                        "drive_link": file_info.get('webViewLink'),
                        "created_at": file_info.get('createdTime'),
                        "file_size": int(file_info.get('size', 0))
                    })
            
            logger.info(f"Retrieved {len(files)} files from Drive")
            return files
            
        except Exception as e:
            logger.error(f"Failed to list Drive files: {e}")
            raise Exception(f"Failed to list files: {str(e)}")

# Global service instance
drive_service = DriveService()

def get_drive_service() -> DriveService:
    """Get Drive service instance"""
    return drive_service
