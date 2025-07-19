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

# Import the separate job scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper_module.job_scraper import JobScraper


class GmailAPI:
    """Gmail API client for reading emails and managing labels."""
    
    def __init__(self):
        self.service = None
        self.job_scraper = JobScraper()  # Separate scraper instance
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
                    CREDENTIALS_FILE, GMAIL_SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for future use
            with open(TOKEN_FILE, 'wb') as token_file:
                pickle.dump(creds, token_file)
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail API authenticated successfully")
    
    def list_messages(self, query: str = "", max_results: int = 10) -> List[Dict[str, str]]:
        """
        List Gmail messages based on search query.
        
        Args:
            query: Gmail search query (e.g., "from:linkedin.com")
            max_results: Maximum number of messages to return
            
        Returns:
            List of message dictionaries with basic info
        """
        try:
            # Search for messages
            results = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get detailed info for each message
            detailed_messages = []
            for message in messages:
                msg_detail = self.service.users().messages().get(
                    userId='me', 
                    id=message['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                # Extract headers
                headers = {h['name']: h['value'] for h in msg_detail.get('payload', {}).get('headers', [])}
                
                detailed_messages.append({
                    'id': message['id'],
                    'subject': headers.get('Subject', 'No Subject'),
                    'from': headers.get('From', 'Unknown Sender'),
                    'date': headers.get('Date', 'Unknown Date'),
                    'snippet': msg_detail.get('snippet', '')
                })
            
            print(f"✅ Found {len(detailed_messages)} messages")
            return detailed_messages
            
        except HttpError as error:
            print(f"❌ Error listing messages: {error}")
            return []
    
    def get_message_content(self, message_id: str) -> Optional[str]:
        """
        Get the full text content of a Gmail message.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Plain text content of the message or None if failed
        """
        try:
            print(f"✅ Gmail API authenticated successfully")
            
            # Get the message
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            print(f"✅ Retrieved message content")
            
            # Extract text content from message payload
            content = self._extract_text_from_payload(message['payload'])
            
            if content:
                print(f"✅ Retrieved message content ({len(content)} characters)")
                return content
            else:
                print("❌ No text content found in message")
                return None
                
        except Exception as e:
            print(f"❌ Error retrieving message: {e}")
            return None
    
    def add_label(self, message_id: str, label_name: str) -> bool:
        """
        Add a label to a Gmail message.
        
        Args:
            message_id: Gmail message ID
            label_name: Name of the label to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First check if label exists, create if not
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
            
        except Exception as e:
            print(f"❌ Error adding label: {e}")
            return False
    
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
    
    def scrape_job_page(self, job_url: str, max_content_length: int = 2000) -> Optional[Dict[str, str]]:
        """
        Scrape a LinkedIn job page using the separate JobScraper.
        
        Args:
            job_url: LinkedIn job URL to scrape
            max_content_length: Maximum content length to return
            
        Returns:
            Dictionary with job details
        """
        return self.job_scraper.scrape_job_page(job_url, max_content_length)
    
    def get_job_details_from_email(self, message_id: str) -> List[Dict[str, str]]:
        """
        Extract job URLs from email and scrape job details.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            List of job details dictionaries
        """
        # Extract URLs from email
        job_urls = self.extract_job_urls(message_id)
        
        if not job_urls:
            print("No job URLs found in email")
            return []
        
        job_details = []
        for job_url_info in job_urls:
            url = job_url_info['url']
            
            # Scrape job page using separate scraper
            job_data = self.scrape_job_page(url)
            
            if job_data:
                # Add email context
                job_data['link_text'] = job_url_info['link_text']
                job_data['email_id'] = message_id
                job_details.append(job_data)
        
        return job_details
    
    def _get_or_create_label(self, label_name: str) -> Optional[str]:
        """Get existing label or create new one."""
        try:
            # List existing labels
            labels_result = self.service.users().labels().list(userId='me').execute()
            labels = labels_result.get('labels', [])
            
            # Check if label exists
            for label in labels:
                if label['name'] == label_name:
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
            print(f"❌ Error with label operation: {error}")
            return None
    
    def _extract_text_from_payload(self, payload: Dict) -> str:
        """Extract plain text from message payload."""
        content = ""
        
        if payload.get('body', {}).get('data'):
            # Single part message
            content = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8', errors='ignore')
        elif payload.get('parts'):
            # Multi-part message
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    if part.get('body', {}).get('data'):
                        part_content = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
                        content += part_content
                elif part.get('parts'):
                    # Nested parts
                    content += self._extract_text_from_payload(part)
        
        return content
    
    def _extract_html_from_payload(self, payload: Dict) -> str:
        """Extract HTML content from message payload."""
        content = ""
        
        if payload.get('body', {}).get('data') and payload.get('mimeType') == 'text/html':
            # Single HTML part
            content = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8', errors='ignore')
        elif payload.get('parts'):
            # Multi-part message
            for part in payload['parts']:
                if part.get('mimeType') == 'text/html':
                    if part.get('body', {}).get('data'):
                        part_content = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
                        content += part_content
                elif part.get('parts'):
                    # Nested parts
                    content += self._extract_html_from_payload(part)
        
        return content
    
    def _extract_urls_from_text(self, content: str) -> List[Dict[str, str]]:
        """Extract LinkedIn job URLs from plain text content."""
        job_urls = []
        
        # LinkedIn job URL patterns
        patterns = [
            r'https://[^/]*linkedin\.com/jobs/view/\d+[^\s]*',
            r'https://[^/]*linkedin\.com/comm/jobs/view/\d+[^\s]*',
            r'https://[^/]*linkedin\.com/jobs-guest/jobs/view/\d+[^\s]*'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                url = match.group(0)
                # Clean URL
                url = url.rstrip('.,;)')  # Remove trailing punctuation
                
                job_urls.append({
                    'url': url,
                    'link_text': 'View Job'  # Default for text extraction
                })
        
        return job_urls
    
    def _extract_urls_from_html(self, html_content: str) -> List[Dict[str, str]]:
        """Extract LinkedIn job URLs from HTML content using BeautifulSoup."""
        job_urls = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                link_text = link.get_text(strip=True)
                
                # Check if it's a LinkedIn job URL
                linkedin_patterns = [
                    r'linkedin\.com/jobs/view/\d+',
                    r'linkedin\.com/comm/jobs/view/\d+',
                    r'linkedin\.com/jobs-guest/jobs/view/\d+'
                ]
                
                for pattern in linkedin_patterns:
                    if re.search(pattern, href, re.IGNORECASE):
                        job_urls.append({
                            'url': href,
                            'link_text': link_text or 'View Job'
                        })
                        break
        
        except Exception as e:
            print(f"⚠️ Error parsing HTML: {e}")
        
        return job_urls 