"""
SoulCoreHub Email Crawler
------------------------
Utility for crawling websites and social media to find business and public email addresses.
Used by marketing agents to build targeted email lists for campaigns.
"""

import os
import re
import json
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailCrawler:
    def __init__(self):
        """Initialize the email crawler"""
        self.visited_urls = set()
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.s3_client = boto3.client(
            's3',
            region_name='us-east-1',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.memory_bucket = os.getenv('MEMORY_BUCKET')
        
    def crawl_website(self, start_url, max_pages=10, max_depth=2):
        """
        Crawl a website to find email addresses
        
        Args:
            start_url (str): URL to start crawling from
            max_pages (int): Maximum number of pages to crawl
            max_depth (int): Maximum depth to crawl
            
        Returns:
            list: List of found email addresses
        """
        self.visited_urls = set()
        found_emails = set()
        
        def crawl(url, depth):
            if depth > max_depth or len(self.visited_urls) >= max_pages:
                return
                
            if url in self.visited_urls:
                return
                
            self.visited_urls.add(url)
            
            try:
                print(f"Crawling: {url}")
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"Failed to fetch {url}: {response.status_code}")
                    return
                    
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract emails from page
                emails = self.extract_emails(response.text)
                for email in emails:
                    found_emails.add(email)
                
                # Find links to crawl
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    
                    # Skip non-HTTP links
                    if href.startswith('mailto:') or href.startswith('tel:') or href.startswith('#'):
                        continue
                        
                    # Convert relative URL to absolute
                    if not href.startswith('http'):
                        href = urljoin(url, href)
                    
                    # Stay on the same domain
                    if urlparse(href).netloc != urlparse(url).netloc:
                        continue
                    
                    # Crawl the link
                    if href not in self.visited_urls and len(self.visited_urls) < max_pages:
                        # Add a small delay to be polite
                        time.sleep(random.uniform(1, 3))
                        crawl(href, depth + 1)
                        
            except Exception as e:
                print(f"Error crawling {url}: {e}")
        
        # Start crawling
        crawl(start_url, 0)
        
        return list(found_emails)
    
    def crawl_social_media(self, platform, search_terms, max_results=50):
        """
        Crawl social media platforms for email addresses
        
        Args:
            platform (str): Social media platform (twitter, linkedin, etc.)
            search_terms (list): List of search terms
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of found email addresses
        """
        found_emails = set()
        
        # Select the appropriate crawler based on platform
        if platform == 'twitter':
            emails = self._crawl_twitter(search_terms, max_results)
        elif platform == 'linkedin':
            emails = self._crawl_linkedin(search_terms, max_results)
        elif platform == 'github':
            emails = self._crawl_github(search_terms, max_results)
        elif platform == 'reddit':
            emails = self._crawl_reddit(search_terms, max_results)
        else:
            print(f"Unsupported platform: {platform}")
            return []
            
        for email in emails:
            found_emails.add(email)
            
        return list(found_emails)
    
    def extract_emails(self, text):
        """
        Extract email addresses from text
        
        Args:
            text (str): Text to extract emails from
            
        Returns:
            list: List of found email addresses
        """
        emails = self.email_pattern.findall(text)
        
        # Filter out common false positives and non-business emails
        filtered_emails = []
        for email in emails:
            # Skip common false positives
            if 'example.com' in email or 'domain.com' in email:
                continue
                
            # Skip common non-business domains
            if any(domain in email.lower() for domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']):
                # Only include these if they appear to be business-related
                if not any(term in email.lower() for term in ['business', 'admin', 'contact', 'info', 'support']):
                    continue
                    
            filtered_emails.append(email)
            
        return filtered_emails
    
    def validate_email(self, email):
        """
        Validate an email address (basic validation)
        
        Args:
            email (str): Email address to validate
            
        Returns:
            bool: True if email is valid, False otherwise
        """
        # Basic validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False
            
        # Check domain
        domain = email.split('@')[1]
        try:
            import socket
            socket.gethostbyname(domain)
            return True
        except:
            return False
    
    def save_emails(self, emails, category):
        """
        Save found emails to S3
        
        Args:
            emails (list): List of email addresses
            category (str): Category for the emails
            
        Returns:
            bool: Success status
        """
        try:
            # Load existing emails
            try:
                response = self.s3_client.get_object(
                    Bucket=self.memory_bucket,
                    Key=f"marketing/email_lists/{category}.json"
                )
                existing_data = json.loads(response['Body'].read().decode('utf-8'))
                existing_emails = existing_data.get('emails', [])
            except:
                existing_emails = []
                
            # Add new emails
            all_emails = list(set(existing_emails + emails))
            
            # Save to S3
            self.s3_client.put_object(
                Bucket=self.memory_bucket,
                Key=f"marketing/email_lists/{category}.json",
                Body=json.dumps({
                    'category': category,
                    'updated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'count': len(all_emails),
                    'emails': all_emails
                }),
                ContentType='application/json'
            )
            
            return True
            
        except Exception as e:
            print(f"Error saving emails: {e}")
            return False
    
    # Platform-specific crawlers
    def _crawl_twitter(self, search_terms, max_results):
        """Crawl Twitter for email addresses"""
        # This is a placeholder - in a real implementation, you would:
        # 1. Use Twitter API to search for profiles matching search_terms
        # 2. Extract emails from bios and recent tweets
        
        # Simulate finding emails
        return [f"twitter_user{i}@company{i}.com" for i in range(min(max_results, 20))]
    
    def _crawl_linkedin(self, search_terms, max_results):
        """Crawl LinkedIn for email addresses"""
        # This is a placeholder - in a real implementation, you would:
        # 1. Use LinkedIn API to search for profiles matching search_terms
        # 2. Extract contact information
        
        # Simulate finding emails
        return [f"linkedin_user{i}@company{i}.com" for i in range(min(max_results, 15))]
    
    def _crawl_github(self, search_terms, max_results):
        """Crawl GitHub for email addresses"""
        # This is a placeholder - in a real implementation, you would:
        # 1. Use GitHub API to search for users and repositories matching search_terms
        # 2. Extract public emails from profiles
        
        # Simulate finding emails
        return [f"github_user{i}@company{i}.com" for i in range(min(max_results, 25))]
    
    def _crawl_reddit(self, search_terms, max_results):
        """Crawl Reddit for email addresses"""
        # This is a placeholder - in a real implementation, you would:
        # 1. Use Reddit API to search for posts and comments matching search_terms
        # 2. Extract emails from content
        
        # Simulate finding emails
        return [f"reddit_user{i}@company{i}.com" for i in range(min(max_results, 10))]


# Example usage
if __name__ == "__main__":
    crawler = EmailCrawler()
    
    # Crawl a website
    emails = crawler.crawl_website("https://example.com", max_pages=5)
    print(f"Found {len(emails)} emails on website")
    
    # Crawl social media
    twitter_emails = crawler.crawl_social_media("twitter", ["AI", "machine learning"], max_results=20)
    print(f"Found {len(twitter_emails)} emails on Twitter")
    
    # Save emails
    crawler.save_emails(emails + twitter_emails, "ai_developers")
