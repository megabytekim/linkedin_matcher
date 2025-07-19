#!/usr/bin/env python3
"""Unit tests for JobScraper class using mocking."""

import unittest
import asyncio
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
        self.assertIsNotNone(self.scraper.min_delay)
        self.assertIsNotNone(self.scraper.max_delay)
        self.assertIsNone(self.scraper.browser)
        self.assertIsNone(self.scraper.page)
    
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
    
    def test_convert_to_guest_url_invalid_url(self):
        """Test conversion with invalid URL raises ValueError."""
        invalid_url = 'https://google.com'
        
        with self.assertRaises(ValueError):
            self.scraper._convert_to_guest_url(invalid_url)
    
    def test_rate_limiting_delays(self):
        """Test that rate limiting delays are within expected range."""
        self.assertGreaterEqual(self.scraper.min_delay, 0)
        self.assertGreaterEqual(self.scraper.max_delay, self.scraper.min_delay)
        self.assertLessEqual(self.scraper.max_delay, 10)  # Should not be too long


class TestJobScraperIntegration(unittest.TestCase):
    """Integration tests for JobScraper class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.scraper = JobScraper()
    
    def test_url_validation_and_conversion_workflow(self):
        """Test the workflow of URL validation followed by conversion."""
        # Test valid URL workflow
        valid_url = 'https://www.linkedin.com/jobs/view/1234567890/'
        
        # Step 1: Validate URL
        is_valid = self.scraper.validate_linkedin_url(valid_url)
        self.assertTrue(is_valid)
        
        # Step 2: Convert to guest URL
        if is_valid:
            guest_url = self.scraper._convert_to_guest_url(valid_url)
            self.assertEqual(guest_url, 'https://www.linkedin.com/jobs-guest/jobs/view/1234567890/')
        
        # Test invalid URL workflow
        invalid_url = 'https://google.com'
        
        # Step 1: Validate URL
        is_valid = self.scraper.validate_linkedin_url(invalid_url)
        self.assertFalse(is_valid)
        
        # Step 2: Should not convert invalid URL
        if not is_valid:
            with self.assertRaises(ValueError):
                self.scraper._convert_to_guest_url(invalid_url)
    
    def test_guest_url_validation(self):
        """Test that guest URLs are also validated correctly."""
        guest_url = 'https://www.linkedin.com/jobs-guest/jobs/view/1234567890/'
        
        # Guest URLs should be valid
        self.assertTrue(self.scraper.validate_linkedin_url(guest_url))
        
        # Converting guest URL should return the same URL
        converted = self.scraper._convert_to_guest_url(guest_url)
        self.assertEqual(converted, guest_url)


def run_tests():
    """Run all tests."""
    print("🧪 Running Job Scraper Module Unit Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestJobScraperUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestJobScraperIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    run_tests() 