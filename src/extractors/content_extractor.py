from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import time
import json
from urllib.parse import urljoin, urlparse
import re
import platform

class WebContentExtractor:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Initialize Chrome driver with optimal settings for Apple Silicon"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            
            # Handle Apple Silicon Macs and general WebDriver setup
            try:
                # Simplified ChromeDriver setup - removed problematic cache_valid_range parameter
                service = Service(ChromeDriverManager().install())
                
                self.driver = webdriver.Chrome(
                    service=service,
                    options=chrome_options
                )
                self.driver.set_page_load_timeout(30)
                print("✅ WebDriver setup successful")
                
            except Exception as webdriver_error:
                print(f"⚠️ WebDriver setup failed, will use fallback: {webdriver_error}")
                self.driver = None
            
        except Exception as e:
            print(f"❌ WebDriver setup failed: {e}")
            self.driver = None
    
    def extract_website_content(self, url):
        """Enhanced main method to extract all relevant business content"""
        if not self.driver:
            print("❌ WebDriver not available, trying requests fallback")
            return self._fallback_extraction(url)
        
        try:
            print(f"🔄 Loading website: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("✅ Page loaded successfully")
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            # Get page source and create BeautifulSoup object
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            content_data = {
                'url': url,
                'title': self.extract_title(soup),
                'meta_description': self.extract_meta_description(soup),
                'headers': self.extract_headers(soup),
                'navigation': self.extract_navigation(soup),
                'main_content': self.extract_main_content(soup),
                'about_content': self.extract_about_content(soup),
                'services_content': self.extract_services_content(soup),
                'footer_content': self.extract_footer_content(soup),
                'key_phrases': self.extract_key_phrases(soup),
                'business_keywords': self.extract_business_keywords(soup)
            }
            
            print(f"✅ Content extraction completed: {len(content_data)} sections")
            return content_data
            
        except Exception as e:
            print(f"❌ Selenium extraction failed: {str(e)}")
            return self._fallback_extraction(url)
    
    def extract_business_keywords(self, soup):
        """Extract business-specific keywords that indicate industry type"""
        all_text = soup.get_text().lower()
        
        # Enhanced keyword patterns for better industry detection
        keyword_patterns = {
            'automotive': [
                'car', 'vehicle', 'auto', 'automotive', 'driving', 'tesla', 
                'electric vehicle', 'ev', 'model', 'cybertruck', 'roadster', 
                'charging', 'autopilot', 'electric car', 'battery', 'supercharger',
                'motor', 'engine', 'dealership', 'lease', 'finance'
            ],
            'food_service': [
                'coffee', 'menu', 'drink', 'beverage', 'food', 'restaurant', 
                'cafe', 'ordering', 'pickup', 'dine', 'eat', 'taste', 'flavor', 
                'brew', 'barista', 'kitchen', 'dining', 'meal', 'espresso', 
                'latte', 'cappuccino', 'frappuccino', 'delivery', 'catering'
            ],
            'retail': [
                'store', 'shop', 'buy', 'purchase', 'gift card', 'merchandise', 
                'product', 'retail', 'shopping', 'checkout', 'cart', 'sale', 
                'discount', 'promotion', 'offer', 'deal', 'price', 'shipping'
            ],
            'technology': [
                'software', 'programming', 'development', 'app', 'api', 'code', 
                'system', 'tech', 'digital', 'platform', 'innovation', 'ai', 
                'artificial intelligence', 'cloud', 'data', 'analytics', 'mobile',
                'web', 'internet', 'online', 'digital transformation'
            ],
            'fitness': [
                'gym', 'workout', 'fitness', 'exercise', 'training', 'health', 
                'wellness', 'sports', 'physical', 'membership', 'personal trainer',
                'cardio', 'strength', 'yoga', 'pilates', 'nutrition'
            ],
            'manufacturing': [
                'manufacturing', 'production', 'factory', 'assembly', 'industrial', 
                'machinery', 'supply chain', 'quality', 'process', 'automation'
            ],
            'energy': [
                'energy', 'solar', 'renewable', 'sustainable', 'power', 
                'electricity', 'grid', 'battery storage', 'clean energy',
                'wind', 'hydroelectric', 'nuclear', 'fossil fuel'
            ],
            'real_estate': [
                'property', 'real estate', 'home', 'house', 'rental', 'lease', 
                'apartment', 'buy', 'sell', 'mortgage', 'investment', 'commercial'
            ],
            'apparel': [
                'clothing', 'apparel', 'fashion', 'wear', 'style', 'outfit', 
                'shoes', 'athletic', 'sportswear', 'accessories', 'designer'
            ],
            'finance': [
                'bank', 'banking', 'finance', 'financial', 'investment', 'loan',
                'credit', 'insurance', 'wealth', 'money', 'payment', 'trading'
            ],
            'healthcare': [
                'health', 'medical', 'hospital', 'doctor', 'patient', 'treatment',
                'medicine', 'pharmaceutical', 'clinic', 'therapy', 'care'
            ]
        }
        
        keyword_scores = {}
        for category, keywords in keyword_patterns.items():
            score = sum(all_text.count(keyword) for keyword in keywords)
            keyword_scores[category] = score
        
        return keyword_scores
    
    def _fallback_extraction(self, url):
        """Enhanced fallback extraction using requests with better error handling"""
        try:
            print("🔄 Trying requests fallback...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content_data = {
                'url': url,
                'title': self.extract_title(soup),
                'meta_description': self.extract_meta_description(soup),
                'headers': self.extract_headers(soup),
                'navigation': self.extract_navigation(soup),
                'main_content': self.extract_main_content(soup),
                'about_content': self.extract_about_content(soup),
                'services_content': self.extract_services_content(soup),
                'footer_content': self.extract_footer_content(soup),
                'key_phrases': self.extract_key_phrases(soup),
                'business_keywords': self.extract_business_keywords(soup)
            }
            
            print(f"✅ Fallback extraction successful")
            return content_data
            
        except Exception as e:
            print(f"❌ Fallback extraction also failed: {str(e)}")
            return None
    
    def extract_title(self, soup):
        """Extract page title with better handling"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Fallback to Open Graph title
        og_title = soup.find('meta', property='og:title')
        if og_title:
            return og_title.get('content', '').strip()
        
        return ""
    
    def extract_meta_description(self, soup):
        """Extract meta description with fallbacks"""
        # Standard meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        
        # Open Graph description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            return og_desc.get('content', '').strip()
        
        # Twitter description
        twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
        if twitter_desc:
            return twitter_desc.get('content', '').strip()
        
        return ""
    
    def extract_headers(self, soup):
        """Extract all header tags (H1-H6) with improved filtering"""
        headers = {}
        for i in range(1, 7):
            header_tags = soup.find_all(f'h{i}')
            header_texts = []
            for tag in header_tags:
                text = tag.get_text().strip()
                if text and len(text) > 2 and len(text) < 200:  # Filter out very short or very long headers
                    header_texts.append(text)
            headers[f'h{i}'] = header_texts
        return headers
    
    def extract_navigation(self, soup):
        """Enhanced navigation extraction"""
        nav_items = []
        
        # Look for common navigation selectors
        nav_selectors = [
            'nav', '.nav', '.navigation', '.menu', 'header nav',
            '.navbar', '.main-nav', '.primary-nav', '.top-nav',
            '[role="navigation"]', '.site-nav'
        ]
        
        for selector in nav_selectors:
            nav_elements = soup.select(selector)
            for nav in nav_elements:
                links = nav.find_all('a')
                for link in links:
                    text = link.get_text().strip()
                    if text and 3 <= len(text) <= 50:  # Reasonable length for nav items
                        nav_items.append(text)
        
        # Remove duplicates and limit
        unique_nav_items = list(dict.fromkeys(nav_items))  # Preserves order
        return unique_nav_items[:15]
    
    def extract_main_content(self, soup):
        """Enhanced main content extraction"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Look for main content containers
        main_selectors = [
            'main', '.main', '#main', '.content', '#content', 
            '.main-content', 'article', '.post-content', '.page-content',
            '[role="main"]', '.site-content', '.primary-content'
        ]
        
        content_text = ""
        for selector in main_selectors:
            elements = soup.select(selector)
            for element in elements:
                content_text += element.get_text() + " "
        
        # If no specific main content found, get body text
        if not content_text.strip():
            content_text = soup.get_text()
        
        return self.clean_text(content_text)[:3000]  # Increased limit
    
    def extract_about_content(self, soup):
        """Enhanced about content extraction"""
        about_selectors = [
            '.about', '#about', '.about-us', '#about-us', 
            '.company', '.who-we-are', '.our-story', '.mission',
            '.vision', '.values', '.company-info'
        ]
        
        about_content = ""
        for selector in about_selectors:
            elements = soup.select(selector)
            for element in elements:
                about_content += element.get_text() + " "
        
        return self.clean_text(about_content)[:1500] if about_content.strip() else ""
    
    def extract_services_content(self, soup):
        """Enhanced services/products content extraction"""
        service_keywords = [
            'services', 'products', 'offerings', 'solutions', 'what-we-do', 
            'models', 'vehicles', 'portfolio', 'capabilities', 'features'
        ]
        service_content = ""
        
        for keyword in service_keywords:
            # Look for sections with service keywords
            service_sections = soup.find_all(
                ['div', 'section', 'article'], 
                class_=re.compile(keyword, re.I)
            )
            for section in service_sections:
                service_content += section.get_text() + " "
        
        return self.clean_text(service_content)[:1500] if service_content.strip() else ""
    
    def extract_footer_content(self, soup):
        """Enhanced footer extraction"""
        footer = soup.find('footer')
        if footer:
            return self.clean_text(footer.get_text())[:800]
        
        # Fallback to elements with footer-like classes
        footer_selectors = ['.footer', '#footer', '.site-footer', '.page-footer']
        for selector in footer_selectors:
            footer_element = soup.select_one(selector)
            if footer_element:
                return self.clean_text(footer_element.get_text())[:800]
        
        return ""
    
    def extract_key_phrases(self, soup):
        """Enhanced key phrase extraction"""
        all_text = soup.get_text().lower()
        
        # Enhanced business phrase patterns
        business_patterns = [
            r'\b(?:we (?:provide|offer|specialize|focus|deliver|create)|our (?:mission|goal|purpose|vision))\b[^.]*',
            r'\b(?:leading|premier|top|best|expert|innovative|trusted)\s+\w+\s+(?:in|for|provider|service|company)\b[^.]*',
            r'\b(?:years? of experience|established|founded|since \d{4}|serving|helping)\b[^.]*',
            r'\b(?:accelerating|transforming|revolutionizing|sustainable|electric|innovative|cutting-edge)\b[^.]*',
            r'\b(?:committed to|dedicated to|passionate about|focused on)\b[^.]*'
        ]
        
        key_phrases = []
        for pattern in business_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            # Clean and filter phrases
            for match in matches:
                clean_phrase = self.clean_text(match)
                if 10 <= len(clean_phrase) <= 200:  # Reasonable phrase length
                    key_phrases.append(clean_phrase)
        
        return key_phrases[:8]  # Return top 8 phrases
    
    def clean_text(self, text):
        """Enhanced text cleaning"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        
        # Remove multiple punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text.strip()
    
    def close(self):
        """Enhanced cleanup method"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ WebDriver closed successfully")
            except Exception as e:
                print(f"⚠️ WebDriver cleanup warning: {e}")
        else:
            print("✅ No WebDriver to close")
