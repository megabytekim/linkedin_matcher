"""
Unit tests for Gmail API module.

These tests use mocking to avoid requiring actual Gmail API credentials
and LinkedIn job URLs. They focus on testing the logic and error handling
of the Gmail API integration.
"""

import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
import json
import base64

from gmail_module.gmail_api import GmailAPI


class TestGmailAPIUnit(unittest.TestCase):
    """Unit tests for Gmail API functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the service to avoid API calls
        self.mock_service = Mock()
        
        # Patch the build function to return our mock service
        self.build_patcher = patch('gmail_module.gmail_api.build')
        self.mock_build = self.build_patcher.start()
        self.mock_build.return_value = self.mock_service
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.build_patcher.stop()
    
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_list_messages_success(self, mock_file, mock_pickle_load):
        """Test successful message listing."""
        # Mock authentication
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        
        # Mock API responses
        mock_messages_list = {
            'messages': [
                {'id': 'msg1'},
                {'id': 'msg2'}
            ]
        }
        
        mock_message_detail = {
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'From', 'value': 'test@example.com'},
                    {'name': 'Date', 'value': 'Mon, 1 Jan 2024 10:00:00'}
                ]
            },
            'snippet': 'Test snippet'
        }
        
        self.mock_service.users().messages().list().execute.return_value = mock_messages_list
        self.mock_service.users().messages().get().execute.return_value = mock_message_detail
        
        # Test
        gmail_api = GmailAPI()
        result = gmail_api.list_messages('from:test@example.com', 10)
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], 'msg1')
        self.assertEqual(result[0]['subject'], 'Test Subject')
        self.assertEqual(result[0]['from'], 'test@example.com')
    
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_list_messages_empty_query(self, mock_file, mock_pickle_load):
        """Test message listing with empty query defaults to inbox."""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        
        self.mock_service.users().messages().list().execute.return_value = {'messages': []}
        
        gmail_api = GmailAPI()
        result = gmail_api.list_messages('', 10)
        
        # Should search 'in:inbox' when query is empty
        self.mock_service.users().messages().list.assert_called_with(
            userId='me',
            q='in:inbox',
            maxResults=10
        )
    
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_message_content_success(self, mock_file, mock_pickle_load):
        """Test successful message content retrieval."""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        
        # Mock message with text content
        test_content = "This is test message content"
        encoded_content = base64.urlsafe_b64encode(test_content.encode()).decode()
        
        mock_message = {
            'payload': {
                'mimeType': 'text/plain',
                'body': {
                    'data': encoded_content
                }
            }
        }
        
        self.mock_service.users().messages().get().execute.return_value = mock_message
        
        gmail_api = GmailAPI()
        result = gmail_api.get_message_content('test_msg_id')
        
        self.assertEqual(result, test_content)
    
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_extract_job_urls_from_text(self, mock_file, mock_pickle_load):
        """Test LinkedIn URL extraction from message content."""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        
        # Message with LinkedIn job URLs
        test_content = """
        Check out these jobs:
        https://www.linkedin.com/jobs/view/1234567890/
        https://linkedin.com/jobs/view/9876543210/?utm_source=email
        """
        encoded_content = base64.urlsafe_b64encode(test_content.encode()).decode()
        
        mock_message = {
            'payload': {
                'mimeType': 'text/plain',
                'body': {
                    'data': encoded_content
                }
            }
        }
        
        self.mock_service.users().messages().get().execute.return_value = mock_message
        
        gmail_api = GmailAPI()
        result = gmail_api.extract_job_urls('test_msg_id')
        
        # Should find the LinkedIn URLs
        self.assertEqual(len(result), 2)
        self.assertIn('1234567890', result[0]['url'])
        self.assertIn('9876543210', result[1]['url'])
    
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_add_label_creates_new_label(self, mock_file, mock_pickle_load):
        """Test adding a label creates new label if it doesn't exist."""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        
        # Mock no existing labels
        self.mock_service.users().labels().list().execute.return_value = {'labels': []}
        
        # Mock label creation
        mock_created_label = {'id': 'label_123', 'name': 'Test Label'}
        self.mock_service.users().labels().create().execute.return_value = mock_created_label
        
        # Mock message modification
        self.mock_service.users().messages().modify().execute.return_value = {}
        
        gmail_api = GmailAPI()
        result = gmail_api.add_label('msg_123', 'Test Label')
        
        # Assertions
        self.assertTrue(result)
        self.mock_service.users().labels().create.assert_called_once()
        self.mock_service.users().messages().modify.assert_called_once_with(
            userId='me',
            id='msg_123',
            body={'addLabelIds': ['label_123']}
        )
    
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
        
        gmail_api = GmailAPI()
        
        # Test multipart payload
        test_text = "Hello, this is a test message"
        encoded_text = base64.urlsafe_b64encode(test_text.encode()).decode()
        
        multipart_payload = {
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {'data': encoded_text}
                },
                {
                    'mimeType': 'text/html',
                    'body': {'data': 'some_html_data'}
                }
            ]
        }
        
        result = gmail_api._extract_text_from_payload(multipart_payload)
        self.assertIn("Hello, this is a test message", result)
    
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
            
        gmail_api = GmailAPI()
            
        html_content = '''
        <html>
            <body>
                <a href="https://www.linkedin.com/jobs/view/1234567890/">Software Engineer Position</a>
                <a href="https://example.com/other">Other Link</a>
                <a href="https://linkedin.com/comm/jobs/view/9876543210/">Data Scientist Role</a>
            </body>
        </html>
        '''
        
        result = gmail_api._extract_urls_from_html(html_content)
        
        # Should only extract LinkedIn job URLs
        self.assertEqual(len(result), 2)
        self.assertIn('1234567890', result[0]['url'])
        self.assertIn('9876543210', result[1]['url'])
        self.assertEqual(result[0]['link_text'], 'Software Engineer Position')
        self.assertEqual(result[1]['link_text'], 'Data Scientist Role')


class TestGmailAPIIntegration(unittest.TestCase):
    """Integration tests that can run without API credentials."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_service = Mock()
        
        # Mock the build function
        self.build_patcher = patch('gmail_module.gmail_api.build')
        self.mock_build = self.build_patcher.start()
        self.mock_build.return_value = self.mock_service
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.build_patcher.stop()
    
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_gmail_api_initialization(self, mock_file, mock_pickle_load):
        """Test that GmailAPI initializes without errors."""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        
        # This should not raise any exceptions
        gmail_api = GmailAPI()
        self.assertIsNotNone(gmail_api.service)
    
    @patch('gmail_module.gmail_api.pickle.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_url_patterns_comprehensive(self, mock_file, mock_pickle_load):
        """Test that URL extraction works with various LinkedIn URL formats."""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle_load.return_value = mock_creds
        
        gmail_api = GmailAPI()
        
        test_urls = [
            "https://www.linkedin.com/jobs/view/1234567890/",
            "https://linkedin.com/jobs/view/9876543210",
            "https://www.linkedin.com/comm/jobs/view/1111111111/",
            "https://www.linkedin.com/jobs/view/2222222222/?utm_source=email",
        ]
        
        test_text = "\n".join(test_urls)
        extracted = gmail_api._extract_urls_from_text(test_text)
        
        # All URLs should be found and cleaned
        self.assertEqual(len(extracted), 4)
        for i, extracted_url in enumerate(extracted):
            # URLs should be cleaned (no trailing slashes, no query params)
            self.assertNotIn('?', extracted_url['url'])
            self.assertNotIn('utm_source', extracted_url['url'])


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
    
    return result.wasSuccessful()


if __name__ == '__main__':
    run_tests() 