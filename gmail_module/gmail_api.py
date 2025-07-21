"""Gmail API module for reading emails and managing labels."""

import os
import pickle
import base64
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup

from config import GMAIL_SCOPES, CREDENTIALS_FILE, TOKEN_FILE


class GmailAPI:
    """Gmail API client for reading emails and managing labels."""
    
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None
        
        # Load existing token if available
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, 'rb') as token_file:
                creds = pickle.load(token_file)
        
        # If there are no (valid) credentials available, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not CREDENTIALS_FILE.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {CREDENTIALS_FILE}\n"
                        "Please download credentials.json from Google Cloud Console"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(TOKEN_FILE, 'wb') as token_file:
                pickle.dump(creds, token_file)
        
        # Build the Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Successfully authenticated with Gmail API")
    
    def list_messages(self, query: str = '', max_results: int = 10) -> List[Dict[str, str]]:
        """
        List Gmail messages based on query.
        
        Args:
            query: Gmail search query (e.g., 'from:linkedin.com')
            max_results: Maximum number of messages to return
            
        Returns:
            List of message dictionaries with basic info
        """
        try:
            # If no query provided, get recent messages
            search_query = query if query.strip() else 'in:inbox'
            
            # Search for messages
            results = self.service.users().messages().list(
                userId='me', 
                q=search_query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print(f"No messages found for query: '{search_query}'")
                return []
            
            message_list = []
            for message in messages:
                # Get detailed message info
                msg_detail = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='metadata',
                    metadataHeaders=['Subject', 'From', 'Date']
                ).execute()
                
                headers = msg_detail['payload'].get('headers', [])
                header_dict = {h['name']: h['value'] for h in headers}
                
                message_info = {
                    'id': message['id'],
                    'subject': header_dict.get('Subject', 'No Subject'),
                    'from': header_dict.get('From', 'Unknown Sender'),
                    'date': header_dict.get('Date', 'Unknown Date'),
                    'snippet': msg_detail.get('snippet', '')
                }
                message_list.append(message_info)
            
            print(f"✅ Found {len(message_list)} messages")
            return message_list
            
        except HttpError as error:
            print(f"❌ Gmail API error: {error}")
            return []
    
    def get_message_content(self, message_id: str) -> Optional[str]:
        """
        Get the full text content of a message.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Plain text content of the message
        """
        try:
            # Get the full message
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract text content from payload
            content = self._extract_text_from_payload(message['payload'])
            
            if content:
                print(f"✅ Retrieved message content ({len(content)} characters)")
                return content
            else:
                print("⚠️ No text content found in message")
                return None
                
        except HttpError as error:
            print(f"❌ Error getting message content: {error}")
            return None
    
    def _extract_text_from_payload(self, payload: Dict) -> str:
        """Extract plain text from message payload."""
        content = ""
        
        if 'parts' in payload:
            # Multi-part message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    # Decode base64 content
                    data = part['body']['data']
                    decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    content += decoded + "\n"
                elif 'parts' in part:
                    # Nested parts - recurse
                    content += self._extract_text_from_payload(part)
        else:
            # Single part message
            if payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
                data = payload['body']['data']
                decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                content += decoded
        
        return content.strip()

    def _extract_html_from_payload(self, payload: Dict) -> str:
        """Extract HTML content from message payload."""
        content = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/html' and 'data' in part['body']:
                    data = part['body']['data']
                    decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    content += decoded + "\n"
                elif 'parts' in part:
                    content += self._extract_html_from_payload(part)
        else:
            if payload['mimeType'] == 'text/html' and 'data' in payload['body']:
                data = payload['body']['data']
                decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                content += decoded
        
        return content.strip()
    
    def extract_job_urls(self, message_id: str) -> List[Dict[str, str]]:
        """
        Extract LinkedIn job URLs from email content.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            List of dictionaries with job URLs and link text
        """
        try:
            # Get message content
            content = self.get_message_content(message_id)
            if not content:
                return []
            
            # Also get HTML content for better URL extraction
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id,
                format='full'
            ).execute()
            
            html_content = self._extract_html_from_payload(message['payload'])
            
            # Extract URLs from both text and HTML
            job_urls = []
            
            # Text-based URL extraction
            text_urls = self._extract_urls_from_text(content)
            job_urls.extend(text_urls)
            
            # HTML-based URL extraction (more accurate)
            if html_content:
                html_urls = self._extract_urls_from_html(html_content)
                job_urls.extend(html_urls)
            
            # Remove duplicates while preserving order
            seen_urls = set()
            unique_job_urls = []
            for job_url in job_urls:
                if job_url['url'] not in seen_urls:
                    seen_urls.add(job_url['url'])
                    unique_job_urls.append(job_url)
            
            print(f"✅ Found {len(unique_job_urls)} job URLs in email")
            return unique_job_urls
            
        except Exception as error:
            print(f"❌ Error extracting job URLs: {error}")
            return []
    
    def _get_or_create_label(self, label_name: str) -> Optional[str]:
        """Get existing label or create new one."""
        try:
            # List existing labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            # Check if label already exists
            for label in labels:
                if label['name'] == label_name:
                    print(f"✅ Found existing label: {label_name}")
                    return label['id']
            
            # Create new label
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            created_label = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            print(f"✅ Created new label: {label_name}")
            return created_label['id']
            
        except HttpError as error:
            print(f"❌ Error managing label: {error}")
            return None
    
    def add_label(self, message_id: str, label_name: str) -> bool:
        """
        Add a label to a message.
        
        Args:
            message_id: Gmail message ID
            label_name: Name of the label to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get or create the label
            label_id = self._get_or_create_label(label_name)
            if not label_id:
                return False
            
            # Add label to message
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            
            print(f"✅ Added label '{label_name}' to message")
            return True
            
        except HttpError as error:
            print(f"❌ Error adding label: {error}")
            return False
    
    def _extract_urls_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract LinkedIn job URLs from plain text."""
        job_urls = []
        
        # Enhanced LinkedIn job URL patterns
        patterns = [
            r'https://www\.linkedin\.com/jobs/view/\d+[^\s<>"]*',
            r'https://linkedin\.com/jobs/view/\d+[^\s<>"]*',
            r'https://www\.linkedin\.com/comm/jobs/view/\d+[^\s<>"]*',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Clean up URL (remove tracking parameters)
                clean_url = match.split('?')[0].rstrip('/')
                
                job_urls.append({
                    'url': clean_url,
                    'link_text': f'Job {clean_url.split("/")[-1]}'
                })
        
        return job_urls
    
    def _extract_urls_from_html(self, html: str) -> List[Dict[str, str]]:
        """Extract LinkedIn job URLs from HTML content."""
        job_urls = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                text = link.get_text(strip=True)
                
                # Check if it's a LinkedIn job URL
                if ('linkedin.com/jobs/view/' in href or 
                    'linkedin.com/comm/jobs/view/' in href):
                    
                    # Clean up URL
                    clean_url = href.split('?')[0].rstrip('/')
                    
                    # Use actual link text or generate one
                    link_text = text if text else f'Job {clean_url.split("/")[-1]}'
                    
                    job_urls.append({
                        'url': clean_url,
                        'link_text': link_text
                        })
        
        except Exception as e:
            print(f"⚠️ Error parsing HTML: {e}")
        
        return job_urls 