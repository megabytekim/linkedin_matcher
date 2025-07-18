#!/usr/bin/env python3
"""
LinkedIn Job Scraper using Playwright.

This module provides functionality to scrape LinkedIn job postings
using Playwright with stealth settings to avoid detection.
"""

import asyncio
import re
import time
import random
from datetime import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page


class JobScraper:
    """
    LinkedIn Job Scraper with stealth capabilities.
    
    Features:
    - Converts LinkedIn URLs to guest URLs (no login required)
    - Uses stealth browser settings to avoid detection
    - Implements rate limiting with random delays
    - Extracts comprehensive job information
    - Handles "Show more" button to get full descriptions
    """
    
    def __init__(self, min_delay: float = 2.0, max_delay: float = 5.0):
        """
        Initialize the scraper with rate limiting settings.
        
        Args:
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def _init_browser(self):
        """Initialize browser with stealth settings."""
        if self.browser is None:
            playwright = await async_playwright().start()
            
            # Use stealth browser settings
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images',  # Faster loading
                    '--disable-javascript',  # Disable JS for faster loading
                    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            # Create page with stealth settings
            self.page = await self.browser.new_page()
            
            # Set viewport and user agent
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Add stealth scripts
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)
    
    async def _close_browser(self):
        """Close browser and cleanup."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
    
    def validate_linkedin_url(self, url: str) -> bool:
        """
        Validate if the URL is a LinkedIn job URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid LinkedIn job URL, False otherwise
        """
        if not url:
            return False
        
        # Check if it's a LinkedIn URL
        parsed = urlparse(url)
        if not parsed.netloc or 'linkedin.com' not in parsed.netloc:
            return False
        
        # Check if it's a job URL
        job_patterns = [
            r'/jobs/view/',
            r'/comm/jobs/view/',
            r'/jobs-guest/jobs/view/'
        ]
        
        return any(re.search(pattern, url) for pattern in job_patterns)
    
    def _convert_to_guest_url(self, url: str) -> str:
        """
        Convert LinkedIn job URL to guest URL (no login required).
        
        Args:
            url: Original LinkedIn job URL
            
        Returns:
            Guest URL that can be accessed without login
        """
        # Extract job ID from URL
        job_id_match = re.search(r'/jobs/view/(\d+)', url)
        if not job_id_match:
            raise ValueError(f"Could not extract job ID from URL: {url}")
        
        job_id = job_id_match.group(1)
        return f"https://www.linkedin.com/jobs-guest/jobs/view/{job_id}/"
    
    async def _wait_for_rate_limit(self):
        """Wait for a random amount of time to avoid rate limiting."""
        delay = random.uniform(self.min_delay, self.max_delay)
        print(f"⏳ Rate limiting: sleeping for {delay:.1f} seconds...")
        await asyncio.sleep(delay)
    
    async def scrape_job_page(self, url: str, max_content_length: int = 2000) -> Optional[Dict[str, Any]]:
        """
        Scrape a single LinkedIn job page.
        
        Args:
            url: LinkedIn job URL
            max_content_length: Maximum length for description content
            
        Returns:
            Dictionary with job information or None if failed
        """
        if not self.validate_linkedin_url(url):
            print(f"❌ Invalid LinkedIn job URL: {url}")
            return None

        # Close any existing browser to start fresh
        await self._close_browser()
        
        try:
            # Create fresh browser for each job
            await self._init_browser()
            
            # Convert to guest URL
            guest_url = self._convert_to_guest_url(url)
            print(f"🌐 Scraping job page: {guest_url}")
            
            # Navigate with optimized timeout strategy
            try:
                # Try fast load first with shorter timeout
                await self.page.goto(guest_url, wait_until='domcontentloaded', timeout=15000)
                await asyncio.sleep(1)  # Brief wait for content
            except Exception as e:
                print(f"⚠️  Fast load failed, trying basic load: {str(e)[:50]}...")
                try:
                    # Fallback - just load the page
                    await self.page.goto(guest_url, timeout=10000)
                    await asyncio.sleep(2)
                except Exception as e2:
                    print(f"❌ Page load failed completely: {str(e2)[:50]}...")
                    return None
            
            # Handle any popups/dialogs that appear
            await self._handle_popups()
            
            # Expand the job description to get full content
            await self._expand_job_description()
            
            # Extract job information
            job_data = await self._extract_job_data()
            
            if job_data:
                # Add metadata
                job_data['url'] = url
                job_data['guest_url'] = guest_url
                job_data['scraped_at'] = datetime.now().isoformat()
                
                # Don't truncate descriptions - let them be full length
                # Only truncate if extremely long (over 15000 chars)
                if 'description' in job_data and len(job_data['description']) > 15000:
                    job_data['description'] = job_data['description'][:max_content_length] + "..."
                
                print(f"✅ Successfully scraped job: {job_data.get('title', 'Unknown')}")
                return job_data
            else:
                print("❌ Failed to extract job data")
                return None
                
        except Exception as e:
            print(f"❌ Error scraping job page: {e}")
            return None
        finally:
            # Always close browser after each job to start fresh next time
            await self._close_browser()
    
    async def _handle_popups(self):
        """Handle any popups or dialogs that might appear."""
        try:
            print("🔍 Checking for popups/dialogs...")
            
            # Wait a moment for any popups to appear
            await asyncio.sleep(1)
            
            # Try to close any dialog/modal that might be open
            close_selectors = [
                'button[aria-label="닫기"]',
                'button[aria-label="Close"]',
                'button:has-text("닫기")',
                'button:has-text("Close")',
                '.modal button[type="button"]',
                '[role="dialog"] button'
            ]
            
            for selector in close_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        if await element.is_visible():
                            print(f"🔒 Closing popup with selector: {selector}")
                            await element.click()
                            await asyncio.sleep(0.5)
                            break
                except Exception:
                    continue
                    
            print("✅ Popup handling complete")
            
        except Exception as e:
            print(f"⚠️  Error handling popups: {e}")
    
    async def _expand_job_description(self):
        """
        Click "Show more" button to expand the full job description.
        
        This is crucial because LinkedIn guest pages truncate descriptions
        and require clicking "Show more" to see the complete content.
        """
        try:
            print("🔍 Looking for 'Show more' button...")
            
            # Wait for the page to load
            await asyncio.sleep(1)
            
            # Look for "Show more" button with multiple attempts
            show_more_selectors = [
                'button:has-text("Show more")',
                '[data-tracking-control-name="public_jobs_show-more-html-btn"]',
                '.show-more-less-html__button--more',
                'button[aria-label="Show more"]',
                'button:contains("Show more")'
            ]
            
            clicked = False
            for attempt in range(2):  # Try twice max
                for selector in show_more_selectors:
                    try:
                        # Check if button exists and is visible
                        button = await self.page.wait_for_selector(selector, timeout=3000)
                        if button:
                            # Check if button is visible and clickable
                            is_visible = await button.is_visible()
                            if is_visible:
                                print(f"🔍 Found 'Show more' button (attempt {attempt + 1}), expanding...")
                                await button.click()
                                # Wait for content to expand
                                await asyncio.sleep(2)
                                print("✅ Successfully expanded job description")
                                clicked = True
                                break
                    except Exception:
                        continue
                
                if clicked:
                    break
                    
                # If not clicked, wait a bit and try again
                await asyncio.sleep(1)
            
            if not clicked:
                print("ℹ️  No 'Show more' button found or already expanded")
            
            return clicked
            
        except Exception as e:
            print(f"⚠️  Error expanding description: {e}")
            return False
    
    async def _extract_job_data(self) -> Optional[Dict[str, Any]]:
        """
        Extract job data from the current page.
        
        Returns:
            Dictionary with job information
        """
        try:
            # Extract basic information with better selectors
            title = await self._extract_text('h1, .job-details-jobs-unified-top-card__job-title')
            
            # Try multiple selectors for company name
            company_selectors = [
                'a[href*="company"]',
                '.job-details-jobs-unified-top-card__company-name',
                '.job-details-jobs-unified-top-card__subtitle-primary-grouping',
                'h4 a',
                'main a[href*="company"]'
            ]
            company = ""
            for selector in company_selectors:
                company = await self._extract_text(selector)
                if company and len(company.strip()) > 0:
                    break
            
            # Try multiple selectors for location
            location_selectors = [
                '.job-details-jobs-unified-top-card__bullet',
                'h4 span',
                'main span',
                '[data-test-id="job-location"]'
            ]
            location = ""
            for selector in location_selectors:
                location = await self._extract_text(selector)
                if location and len(location.strip()) > 0:
                    break
            
            # Extract page title (often contains full location info)
            page_title = await self.page.title()
            
            # Extract job description (now expanded)
            description = await self._extract_job_description()
            
            # Extract job details
            job_details = await self._extract_job_details()
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'pageTitle': page_title,
                'jobDetails': job_details
            }
            
        except Exception as e:
            print(f"❌ Error extracting job data: {e}")
            return None
    
    async def _extract_text(self, selector: str) -> str:
        """Extract text from an element using CSS selector."""
        try:
            element = await self.page.query_selector(selector)
            if element:
                return await element.text_content() or ""
            return ""
        except Exception:
            return ""
    
    async def _extract_job_description(self) -> str:
        """
        Extract the full job description after expanding it.
        
        Returns:
            Complete job description text
        """
        try:
            # Wait a bit more for content to load after expansion
            await asyncio.sleep(2)
            
            # Try multiple selectors for the job description
            # Based on the actual LinkedIn guest page structure
            description_selectors = [
                # Main content area after expansion - try these first
                '.show-more-less-html__more-content',
                '.show-more-less-html__less-content', 
                # Alternative selectors for job content
                '.jobs-description__content',
                '.jobs-box__html-content',
                '.job-description',
                '[data-job-description]',
                # More specific selectors for guest pages
                'main div[class*="description"]',
                'main div[class*="content"]'
            ]
            
            for selector in description_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text and len(text.strip()) > 100:  # Ensure we got meaningful content
                            clean_text = text.strip()
                            print(f"✅ Found description with selector: {selector} ({len(clean_text)} chars)")
                            return clean_text
                except Exception:
                    continue
            
            # Enhanced fallback: Extract from the main page content more intelligently
            try:
                print("🔍 Using enhanced main content extraction...")
                
                # Get the entire page text
                page_content = await self.page.text_content()
                if not page_content:
                    return ""
                
                # Split into lines and process
                lines = page_content.split('\n')
                job_lines = []
                
                # Find job-related content by looking for key phrases
                in_job_section = False
                
                for line in lines:
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Start capturing when we see job-related content
                    if any(keyword in line.lower() for keyword in [
                        'minimum qualifications', 'preferred qualifications', 
                        'about the job', 'responsibilities', 'requirements',
                        'job description', 'what you\'ll do', 'qualifications'
                    ]):
                        in_job_section = True
                    
                    # Skip navigation and UI elements
                    if any(skip_phrase in line for skip_phrase in [
                        'LinkedIn', '로그인', '회원가입', 'Sign in', 'Join now',
                        'Apply', 'Save', 'Show more', 'Show less', '©',
                        'About', 'Accessibility', 'Privacy Policy', 'Cookie Policy',
                        'User Agreement', 'Brand Policy', 'Community Guidelines',
                        'Similar jobs', 'People also viewed', 'Get notified'
                    ]):
                        continue
                    
                    # If we're in job section or line looks like job content
                    if (in_job_section or 
                        len(line) > 30 and 
                        any(keyword in line.lower() for keyword in [
                            'experience', 'degree', 'bachelor', 'master', 'phd',
                            'years', 'skills', 'knowledge', 'ability', 'responsible',
                            'manage', 'develop', 'work', 'team', 'project'
                        ])):
                        job_lines.append(line)
                
                if job_lines:
                    description = ' '.join(job_lines)
                    if len(description) > 200:
                        print(f"✅ Found description using enhanced extraction ({len(description)} chars)")
                        return description
                        
            except Exception as e:
                print(f"⚠️  Enhanced extraction failed: {e}")
            
            # Final fallback: try to get any substantial text content
            try:
                main_element = await self.page.query_selector('main')
                if main_element:
                    main_text = await main_element.text_content()
                    if main_text and len(main_text) > 500:
                        # Clean up and return substantial content
                        clean_text = ' '.join(line.strip() for line in main_text.split('\n') 
                                            if line.strip() and len(line.strip()) > 10)
                        if len(clean_text) > 200:
                            print(f"✅ Found description using main element fallback ({len(clean_text)} chars)")
                            return clean_text
                            
            except Exception as e:
                print(f"⚠️  Main element extraction failed: {e}")
            
            print("❌ Could not extract job description with any method")
            return ""
            
        except Exception as e:
            print(f"❌ Error extracting job description: {e}")
            return ""
    
    async def _extract_job_details(self) -> List[str]:
        """Extract job details like seniority, employment type, etc."""
        try:
            details = []
            
            # Look for job criteria elements
            criteria_selectors = [
                '.job-details-jobs-unified-top-card__job-insight',
                '.jobs-box__group',
                '.jobs-description__job-criteria-item'
            ]
            
            for selector in criteria_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        text = await element.text_content()
                        if text:
                            details.append(text.strip())
                except Exception:
                    continue
            
            return details
            
        except Exception as e:
            print(f"❌ Error extracting job details: {e}")
            return []
    
    async def scrape_multiple_jobs(self, urls: List[str], max_content_length: int = 1500) -> List[Dict[str, Any]]:
        """
        Scrape multiple LinkedIn job pages with rate limiting.
        
        Args:
            urls: List of LinkedIn job URLs
            max_content_length: Maximum length for description content
            
        Returns:
            List of job data dictionaries
        """
        if not urls:
            return []
        
        print(f"🌐 Starting to scrape {len(urls)} job pages...")
        print("⚠️ Using fresh browser for each job to avoid conflicts")
        
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n📋 Processing job {i}/{len(urls)}")
            
            try:
                # Each job gets a completely fresh scraper instance
                # This ensures no browser state pollution
                job_data = await self.scrape_job_page(url, max_content_length)
                
                if job_data:
                    results.append(job_data)
                    print(f"✅ Success: {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}")
                else:
                    print(f"❌ Failed to scrape job {i}")
                
                # Add extra delay between multiple jobs
                if i < len(urls):
                    extra_delay = random.uniform(0.5, 1.0)
                    print(f"⏳ Extra delay before next job: {extra_delay:.1f} seconds...")
                    await asyncio.sleep(extra_delay)
                
            except Exception as e:
                print(f"❌ Error processing job {i}: {e}")
                continue
        
        print(f"\n📊 Completed scraping: {len(results)}/{len(urls)} jobs successful")
        return results
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._init_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_browser()


# Convenience functions for synchronous usage
def scrape_job_page(url: str, max_content_length: int = 2000) -> Optional[Dict[str, Any]]:
    """
    Scrape a single LinkedIn job page (synchronous wrapper).
    
    Args:
        url: LinkedIn job URL
        max_content_length: Maximum length for description content
        
    Returns:
        Dictionary with job information or None if failed
    """
    async def _scrape():
        async with JobScraper() as scraper:
            return await scraper.scrape_job_page(url, max_content_length)
    
    return asyncio.run(_scrape())


def scrape_multiple_jobs(urls: List[str], max_content_length: int = 1500) -> List[Dict[str, Any]]:
    """
    Scrape multiple LinkedIn job pages (synchronous wrapper).
    
    Args:
        urls: List of LinkedIn job URLs
        max_content_length: Maximum length for description content
        
    Returns:
        List of job data dictionaries
    """
    async def _scrape():
        async with JobScraper() as scraper:
            return await scraper.scrape_multiple_jobs(urls, max_content_length)
    
    return asyncio.run(_scrape()) 