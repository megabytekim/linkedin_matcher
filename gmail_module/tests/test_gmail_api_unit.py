#!/usr/bin/env python3
"""Unit tests for GmailAPI class using mocking."""

import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
import base64
import pickle
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gmail_module.gmail_api import GmailAPI


class TestGmailAPIUnit(unittest.TestCase):
    """Unit tests for GmailAPI class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the config module
        self.config_patcher = patch('gmail_module.gmail_api.CREDENTIALS_FILE')
        self.token_patcher = patch('gmail_module.gmail_api.TOKEN_FILE')
        self.scopes_patcher = patch('gmail_module.gmail_api.GMAIL_SCOPES')
        
        self.mock_credentials_file = self.config_patcher.start()
        self.mock_token_file = self.token_patcher.start()
        self.mock_scopes = self.scopes_patcher.start()
        
        # Set up mock file paths
        self.mock_credentials_file.exists.return_value = True
        self.mock_token_file.exists.return_value = True
        self.mock_scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        
        # Mock the scraper
        self.scraper_patcher = patch('gmail_module.gmail_api.JobScraper')
        self.mock_scraper_class = self.scraper_patcher.start()
        self.mock_scraper = Mock()
        self.mock_scraper_class.return_value = self.mock_scraper
    
    def tearDown(self):
        """Clean up after each test method."""
        self.config_patcher.stop()
        self.token_patcher.stop()
        self.scopes_patcher.stop()
        self.scraper_patcher.stop()
    
    @patch('gmail_module.gmail_api.build')
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_authentication_with_existing_token(self, mock_file, mock_pickle_load, mock_build):
        """Test authentication with existing valid token."""
        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Create GmailAPI instance
        gmail_api = GmailAPI()
        
        # Assertions
        mock_pickle_load.assert_called_once()
        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)
        self.assertEqual(gmail_api.service, mock_service)
    
    @patch('gmail_module.gmail_api.build')
    @patch('gmail_module.gmail_api.InstalledAppFlow.from_client_secrets_file')
    @patch('gmail_module.gmail_api.pickle.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_authentication_new_credentials(self, mock_file, mock_pickle_dump, mock_flow_class, mock_build):
        """Test authentication with new credentials."""
        # Setup mocks
        self.mock_token_file.exists.return_value = False
        mock_flow = Mock()
        mock_flow_class.return_value = mock_flow
        mock_creds = Mock()
        mock_flow.run_local_server.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Create GmailAPI instance
        gmail_api = GmailAPI()
        
        # Assertions
        mock_flow_class.assert_called_once()
        mock_flow.run_local_server.assert_called_once_with(port=0)
        mock_pickle_dump.assert_called_once()
        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)
    
    @patch('gmail_module.gmail_api.build')
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_list_messages_success(self, mock_file, mock_pickle_load, mock_build):
        """Test successful message listing."""
        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Mock API responses
        mock_list_response = {
            'messages': [
                {'id': 'msg1'},
                {'id': 'msg2'}
            ]
        }
        
        mock_msg_detail_1 = {
            'id': 'msg1',
            'snippet': 'Test message 1',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject 1'},
                    {'name': 'From', 'value': 'test1@linkedin.com'},
                    {'name': 'Date', 'value': '2025-01-18'}
                ]
            }
        }
        
        mock_msg_detail_2 = {
            'id': 'msg2',
            'snippet': 'Test message 2',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject 2'},
                    {'name': 'From', 'value': 'test2@linkedin.com'},
                    {'name': 'Date', 'value': '2025-01-18'}
                ]
            }
        }
        
        mock_service.users().messages().list().execute.return_value = mock_list_response
        mock_service.users().messages().get().execute.side_effect = [mock_msg_detail_1, mock_msg_detail_2]
        
        # Create GmailAPI instance and test
        gmail_api = GmailAPI()
        messages = gmail_api.list_messages(query="from:linkedin.com", max_results=2)
        
        # Assertions
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['id'], 'msg1')
        self.assertEqual(messages[0]['subject'], 'Test Subject 1')
        self.assertEqual(messages[0]['from'], 'test1@linkedin.com')
        self.assertEqual(messages[1]['id'], 'msg2')
    
    @patch('gmail_module.gmail_api.build')
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_message_content_success(self, mock_file, mock_pickle_load, mock_build):
        """Test successful message content retrieval."""
        # Setup mocks
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Create test content
        test_content = "This is a test email content with LinkedIn job URLs."
        encoded_content = base64.urlsafe_b64encode(test_content.encode('utf-8')).decode('utf-8')
        
        mock_message = {
            'payload': {
                'mimeType': 'text/plain',
                'body': {
                    'data': encoded_content
                }
            }
        }
        
        mock_service.users().messages().get().execute.return_value = mock_message
        
        # Create GmailAPI instance and test
        gmail_api = GmailAPI()
        content = gmail_api.get_message_content('test_msg_id')
        
        # Assertions
        self.assertEqual(content, test_content)
        # The service is called to get the message
        mock_service.users().messages().get.assert_called_with(
            userId='me', 
            id='test_msg_id',
            format='full'
        )
    
    @patch('gmail_module.gmail_api.build')
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_extract_urls_from_text(self, mock_file, mock_pickle_load, mock_build):
        """Test URL extraction from plain text."""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Create GmailAPI instance
        gmail_api = GmailAPI()
        
        # Test text with LinkedIn URLs
        test_content = """
        Check out this job: https://www.linkedin.com/jobs/view/1234567890/
        Another opportunity: https://linkedin.com/comm/jobs/view/9876543210/
        Guest URL: https://www.linkedin.com/jobs-guest/jobs/view/1111111111/
        """
        
        urls = gmail_api._extract_urls_from_text(test_content)
        
        # Assertions
        self.assertEqual(len(urls), 3)
        self.assertIn('1234567890', urls[0]['url'])
        self.assertIn('9876543210', urls[1]['url'])
        self.assertIn('1111111111', urls[2]['url'])
        self.assertEqual(urls[0]['link_text'], 'View Job')
    
    @patch('gmail_module.gmail_api.build')
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_extract_urls_from_html(self, mock_file, mock_pickle_load, mock_build):
        """Test URL extraction from HTML content."""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Create GmailAPI instance
        gmail_api = GmailAPI()
        
        # Test HTML with LinkedIn URLs
        test_html = """
        <html>
        <body>
            <a href="https://www.linkedin.com/jobs/view/1234567890/">View Job Position</a>
            <a href="https://linkedin.com/comm/jobs/view/9876543210/">Apply Now</a>
            <a href="https://google.com">Not a job link</a>
        </body>
        </html>
        """
        
        urls = gmail_api._extract_urls_from_html(test_html)
        
        # Assertions
        self.assertEqual(len(urls), 2)
        self.assertIn('1234567890', urls[0]['url'])
        self.assertEqual(urls[0]['link_text'], 'View Job Position')
        self.assertIn('9876543210', urls[1]['url'])
        self.assertEqual(urls[1]['link_text'], 'Apply Now')
    
    @patch('gmail_module.gmail_api.build')
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_add_label_success(self, mock_file, mock_pickle_load, mock_build):
        """Test successful label addition."""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Mock label operations
        mock_labels_response = {
            'labels': [
                {'id': 'label_123', 'name': 'Important'}
            ]
        }
        mock_service.users().labels().list().execute.return_value = mock_labels_response
        mock_service.users().messages().modify().execute.return_value = {}
        
        # Create GmailAPI instance and test
        gmail_api = GmailAPI()
        result = gmail_api.add_label('test_msg_id', 'Important')
        
        # Assertions
        self.assertTrue(result)
        # The service is called to modify the message
        mock_service.users().messages().modify.assert_called_with(
            userId='me',
            id='test_msg_id',
            body={'addLabelIds': ['label_123']}
        )
    
    @patch('gmail_module.gmail_api.build')
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_scrape_job_page_delegation(self, mock_file, mock_pickle_load, mock_build):
        """Test that job scraping is properly delegated to JobScraper."""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Mock scraper response
        mock_job_data = {
            'title': 'Software Engineer',
            'company': 'Test Company',
            'location': 'Seoul, Korea'
        }
        self.mock_scraper.scrape_job_page.return_value = mock_job_data
        
        # Create GmailAPI instance and test
        gmail_api = GmailAPI()
        result = gmail_api.scrape_job_page('https://linkedin.com/jobs/view/123')
        
        # Assertions
        self.assertEqual(result, mock_job_data)
        self.mock_scraper.scrape_job_page.assert_called_once_with('https://linkedin.com/jobs/view/123', 2000)
    
    @patch('gmail_module.gmail_api.build')
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_extract_text_from_multipart_payload(self, mock_file, mock_pickle_load, mock_build):
        """Test text extraction from multipart message payload."""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Create GmailAPI instance
        gmail_api = GmailAPI()
        
        # Test multipart payload
        test_content = "Hello from multipart message"
        encoded_content = base64.urlsafe_b64encode(test_content.encode('utf-8')).decode('utf-8')
        
        payload = {
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {
                        'data': encoded_content
                    }
                },
                {
                    'mimeType': 'text/html',
                    'body': {
                        'data': base64.urlsafe_b64encode(b'<html>HTML content</html>').decode('utf-8')
                    }
                }
            ]
        }
        
        content = gmail_api._extract_text_from_payload(payload)
        
        # Assertions
        self.assertIn('Hello from multipart message', content)
    
    def test_extract_html_from_payload_empty(self):
        """Test HTML extraction from empty payload."""
        # Mock the necessary components without full GmailAPI initialization
        with patch('gmail_module.gmail_api.build'), \
             patch('builtins.open', new_callable=mock_open), \
             patch('gmail_module.gmail_api.pickle.load') as mock_pickle_load:
            
            mock_creds = Mock()
            mock_creds.valid = True
            mock_pickle_load.return_value = mock_creds
            
            gmail_api = GmailAPI()
            
            # Test empty payload
            payload = {}
            content = gmail_api._extract_html_from_payload(payload)
            
            # Assertions
            self.assertEqual(content, "")


class TestGmailAPIIntegration(unittest.TestCase):
    """Integration tests for GmailAPI workflow."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        # Mock all external dependencies
        self.patches = [
            patch('gmail_module.gmail_api.CREDENTIALS_FILE'),
            patch('gmail_module.gmail_api.TOKEN_FILE'),
            patch('gmail_module.gmail_api.GMAIL_SCOPES'),
            patch('gmail_module.gmail_api.JobScraper'),
            patch('gmail_module.gmail_api.build'),
            patch('builtins.open', new_callable=mock_open),
            patch('gmail_module.gmail_api.pickle.load')
        ]
        
        self.mocks = [p.start() for p in self.patches]
        
        # Configure mocks for successful initialization
        self.mocks[0].exists.return_value = True  # credentials file
        self.mocks[1].exists.return_value = True  # token file
        self.mocks[2] = ['https://www.googleapis.com/auth/gmail.readonly']  # scopes
        
        mock_creds = Mock()
        mock_creds.valid = True
        self.mocks[6].return_value = mock_creds  # pickle.load
        
        self.mock_service = Mock()
        self.mocks[4].return_value = self.mock_service  # build
        
        self.mock_scraper = Mock()
        self.mocks[3].return_value = self.mock_scraper  # JobScraper
    
    def tearDown(self):
        """Clean up integration test fixtures."""
        for p in self.patches:
            p.stop()
    
    def test_complete_workflow_email_to_job_data(self):
        """Test complete workflow from email to job data."""
        # Setup email with job URLs
        test_content = """
        New job opportunity for you!
        Check it out: https://www.linkedin.com/jobs/view/1234567890/
        """
        encoded_content = base64.urlsafe_b64encode(test_content.encode('utf-8')).decode('utf-8')
        
        mock_message = {
            'payload': {
                'mimeType': 'text/plain',
                'body': {
                    'data': encoded_content
                }
            }
        }
        
        mock_job_data = {
            'title': 'Senior ML Engineer',
            'company': 'Tech Corp',
            'location': 'Seoul, Korea',
            'url': 'https://www.linkedin.com/jobs/view/1234567890/'
        }
        
        # Configure service mocks
        self.mock_service.users().messages().get().execute.return_value = mock_message
        self.mock_scraper.scrape_job_page.return_value = mock_job_data
        
        # Test workflow
        gmail_api = GmailAPI()
        job_details = gmail_api.get_job_details_from_email('test_msg_id')
        
        # Assertions
        self.assertEqual(len(job_details), 1)
        self.assertEqual(job_details[0]['title'], 'Senior ML Engineer')
        self.assertEqual(job_details[0]['company'], 'Tech Corp')
        self.assertEqual(job_details[0]['email_id'], 'test_msg_id')
        self.assertIn('link_text', job_details[0])


def run_tests():
    """Run all unit tests."""
    print("🧪 Running Gmail Module Unit Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGmailAPIUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestGmailAPIIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n🎉 All tests passed!" if success else "❌ Some tests failed!")
    return success


if __name__ == '__main__':
    run_tests() 