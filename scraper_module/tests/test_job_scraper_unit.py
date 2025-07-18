#!/usr/bin/env python3
"""Unit tests for JobScraper class using mocking."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scraper_module.job_scraper import JobScraper


class TestJobScraperUnit(unittest.TestCase):
    """Unit tests for JobScraper class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.scraper = JobScraper()
    
    def test_initialization(self):
        """Test JobScraper initialization."""
        self.assertIsNotNone(self.scraper.user_agent)
        self.assertIn('Mozilla', self.scraper.user_agent)
        self.assertIn('Chrome', self.scraper.user_agent)
    
    def test_validate_linkedin_url_valid_urls(self):
        """Test URL validation with valid LinkedIn job URLs."""
        valid_urls = [
            'https://www.linkedin.com/jobs/view/1234567890/',
            'https://linkedin.com/jobs/view/9876543210',
            'https://www.linkedin.com/comm/jobs/view/1111111111/',
            'https://linkedin.com/comm/jobs/view/2222222222',
            'https://www.linkedin.com/jobs-guest/jobs/view/3333333333/'
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(self.scraper.validate_linkedin_url(url))
    
    def test_validate_linkedin_url_invalid_urls(self):
        """Test URL validation with invalid URLs."""
        invalid_urls = [
            'https://google.com',
            'https://linkedin.com/profile/user',
            'https://www.linkedin.com/feed/',
            'https://linkedin.com/jobs/search',
            'https://indeed.com/jobs/view/123',
            'not-a-url',
            ''
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.scraper.validate_linkedin_url(url))
    
    def test_convert_to_guest_url_standard_job_url(self):
        """Test conversion of standard LinkedIn job URL to guest URL."""
        test_cases = [
            {
                'input': 'https://www.linkedin.com/jobs/view/1234567890/',
                'expected': 'https://www.linkedin.com/jobs-guest/jobs/view/1234567890/'
            },
            {
                'input': 'https://linkedin.com/jobs/view/9876543210',
                'expected': 'https://www.linkedin.com/jobs-guest/jobs/view/9876543210/'
            },
            {
                'input': 'https://www.linkedin.com/comm/jobs/view/1111111111/',
                'expected': 'https://www.linkedin.com/jobs-guest/jobs/view/1111111111/'
            }
        ]
        
        for case in test_cases:
            with self.subTest(input_url=case['input']):
                result = self.scraper._convert_to_guest_url(case['input'])
                self.assertEqual(result, case['expected'])
    
    def test_convert_to_guest_url_with_tracking_params(self):
        """Test guest URL conversion removes tracking parameters."""
        url_with_params = 'https://www.linkedin.com/jobs/view/1234567890/?utm_source=email&refId=abc123&trackingId=xyz789'
        expected = 'https://www.linkedin.com/jobs-guest/jobs/view/1234567890/'
        
        result = self.scraper._convert_to_guest_url(url_with_params)
        self.assertEqual(result, expected)
    
    def test_convert_to_guest_url_already_guest(self):
        """Test conversion when URL is already a guest URL."""
        guest_url = 'https://www.linkedin.com/jobs-guest/jobs/view/1234567890/'
        result = self.scraper._convert_to_guest_url(guest_url)
        self.assertEqual(result, guest_url)
    
    def test_get_timestamp(self):
        """Test timestamp generation."""
        timestamp = self.scraper._get_timestamp()
        self.assertIsInstance(timestamp, str)
        self.assertIn('T', timestamp)  # ISO format contains 'T'
        self.assertTrue(len(timestamp) > 10)  # Should be a reasonable length
    
    @patch('scraper_module.job_scraper.sync_playwright')
    def test_scrape_job_page_success(self, mock_playwright):
        """Test successful job page scraping."""
        # Setup mock playwright
        mock_playwright_instance = MagicMock()
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance
        
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock page evaluation result
        mock_job_data = {
            'title': 'Senior Software Engineer',
            'company': 'Tech Corporation',
            'location': 'Seoul, South Korea',
            'description': 'We are looking for a senior software engineer with experience in Python and ML.',
            'pageTitle': 'Senior Software Engineer - Tech Corporation | LinkedIn',
            'jobDetails': ['Full-time', 'Remote', 'Senior level']
        }
        
        mock_page.evaluate.return_value = mock_job_data
        
        # Test scraping
        result = self.scraper.scrape_job_page('https://www.linkedin.com/jobs/view/1234567890/')
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Senior Software Engineer')
        self.assertEqual(result['company'], 'Tech Corporation')
        self.assertEqual(result['location'], 'Seoul, South Korea')
        self.assertIn('url', result)
        self.assertIn('guest_url', result)
        self.assertIn('scraped_at', result)
        
        # Verify playwright calls
        mock_playwright_instance.chromium.launch.assert_called_once_with(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage'
            ]
        )
        mock_browser.new_context.assert_called_once()
        mock_context.new_page.assert_called_once()
        mock_page.goto.assert_called_once()
        mock_page.evaluate.assert_called_once()
        mock_browser.close.assert_called_once()
    
    @patch('scraper_module.job_scraper.sync_playwright')
    def test_scrape_job_page_with_content_length_limit(self, mock_playwright):
        """Test job page scraping with content length limit."""
        # Setup mock playwright
        mock_playwright_instance = MagicMock()
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance
        
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock long description
        long_description = 'A' * 5000  # 5000 characters
        mock_job_data = {
            'title': 'Test Job',
            'company': 'Test Company',
            'location': 'Test Location',
            'description': long_description,
            'pageTitle': 'Test Job | LinkedIn',
            'jobDetails': []
        }
        
        mock_page.evaluate.return_value = mock_job_data
        
        # Test with content limit
        max_length = 100
        result = self.scraper.scrape_job_page(
            'https://www.linkedin.com/jobs/view/1234567890/', 
            max_content_length=max_length
        )
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertTrue(len(result['description']) <= max_length + 3)  # +3 for "..."
        self.assertTrue(result['description'].endswith('...'))
    
    @patch('scraper_module.job_scraper.sync_playwright')
    def test_scrape_job_page_error_handling(self, mock_playwright):
        """Test error handling during job page scraping."""
        # Setup mock to raise exception
        mock_playwright.side_effect = Exception("Network error")
        
        # Test scraping with error
        result = self.scraper.scrape_job_page('https://www.linkedin.com/jobs/view/1234567890/')
        
        # Assertions
        self.assertIsNone(result)
    
    @patch('scraper_module.job_scraper.sync_playwright')
    def test_scrape_multiple_jobs_success(self, mock_playwright):
        """Test scraping multiple job pages successfully."""
        # Setup mock playwright
        mock_playwright_instance = MagicMock()
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance
        
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # Mock different job data for each URL
        job_data_responses = [
            {
                'title': 'Job 1',
                'company': 'Company 1',
                'location': 'Location 1',
                'description': 'Description 1',
                'pageTitle': 'Job 1 | LinkedIn',
                'jobDetails': []
            },
            {
                'title': 'Job 2',
                'company': 'Company 2',
                'location': 'Location 2',
                'description': 'Description 2',
                'pageTitle': 'Job 2 | LinkedIn',
                'jobDetails': []
            }
        ]
        
        mock_page.evaluate.side_effect = job_data_responses
        
        # Test multiple job scraping
        urls = [
            'https://www.linkedin.com/jobs/view/1111111111/',
            'https://www.linkedin.com/jobs/view/2222222222/'
        ]
        
        results = self.scraper.scrape_multiple_jobs(urls)
        
        # Assertions
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Job 1')
        self.assertEqual(results[1]['title'], 'Job 2')
        self.assertEqual(results[0]['company'], 'Company 1')
        self.assertEqual(results[1]['company'], 'Company 2')
    
    @patch('scraper_module.job_scraper.sync_playwright')
    def test_scrape_multiple_jobs_partial_failure(self, mock_playwright):
        """Test scraping multiple jobs with some failures."""
        # Setup mock to simulate partial failure
        mock_playwright_instance = MagicMock()
        mock_playwright.return_value.__enter__.return_value = mock_playwright_instance
        
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # First call succeeds, second call fails
        mock_page.evaluate.side_effect = [
            {
                'title': 'Successful Job',
                'company': 'Good Company',
                'location': 'Seoul',
                'description': 'Good description',
                'pageTitle': 'Job | LinkedIn',
                'jobDetails': []
            },
            Exception("Scraping failed")
        ]
        
        urls = [
            'https://www.linkedin.com/jobs/view/1111111111/',
            'https://www.linkedin.com/jobs/view/2222222222/'
        ]
        
        results = self.scraper.scrape_multiple_jobs(urls)
        
        # Assertions - should only return successful scrapes
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Successful Job')


class TestJobScraperIntegration(unittest.TestCase):
    """Integration tests for JobScraper workflow."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.scraper = JobScraper()
    
    def test_url_validation_and_conversion_workflow(self):
        """Test the workflow of URL validation followed by conversion."""
        test_url = 'https://www.linkedin.com/jobs/view/1234567890/?utm_source=email'
        
        # Test validation
        is_valid = self.scraper.validate_linkedin_url(test_url)
        self.assertTrue(is_valid)
        
        # Test conversion
        guest_url = self.scraper._convert_to_guest_url(test_url)
        expected_guest_url = 'https://www.linkedin.com/jobs-guest/jobs/view/1234567890/'
        self.assertEqual(guest_url, expected_guest_url)
        
        # Verify guest URL is also valid
        guest_is_valid = self.scraper.validate_linkedin_url(guest_url)
        self.assertTrue(guest_is_valid)


def run_tests():
    """Run all scraper unit tests."""
    print("🧪 Running Job Scraper Module Unit Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestJobScraperUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestJobScraperIntegration))
    
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