"""
Batch processing for multiple company classifications
"""
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import logging
from datetime import datetime
import json

from src.extractors.content_extractor import ContentExtractor
from src.classifiers.naics_classifier import NAICSClassifier
from src.database.manager import db_manager
from config.settings import Settings

class BatchProcessor:
    def __init__(self):
        self.extractor = ContentExtractor()
        self.classifier = NAICSClassifier()
        self.logger = logging.getLogger(__name__)
        self.max_workers = 10
        self.semaphore = asyncio.Semaphore(20)  # Limit concurrent requests
    
    def process_batch(self, items: List[Dict], session_id: str = None, user_id: str = None):
        """Process a batch of items synchronously"""
        session = None
        if session_id or user_id:
            session = db_manager.create_analysis_session({
                'session_name': f'Batch_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'user_id': user_id,
                'batch_size': len(items),
                'status': 'running'
            })
            session_id = session.id
        
        try:
            results = []
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_item = {
                    executor.submit(self._process_single_item, item, i): (item, i)
                    for i, item in enumerate(items)
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_item):
                    item, index = future_to_item[future]
                    try:
                        result = future.result()
                        result['index'] = index
                        results.append(result)
                        
                        # Save to database if session exists
                        if session_id and result.get('classification'):
                            self._save_result_to_db(result, session_id)
                            
                    except Exception as e:
                        self.logger.error(f"Error processing item {index}: {str(e)}")
                        results.append({
                            'index': index,
                            'error': str(e),
                            'status': 'error'
                        })
            
            # Update session status
            if session:
                summary = self._generate_batch_summary(results)
                db_manager.update_session_status(session_id, 'completed', summary)
            
            return {
                'results': sorted(results, key=lambda x: x['index']),
                'summary': self._generate_batch_summary(results),
                'session_id': session_id
            }
            
        except Exception as e:
            if session:
                db_manager.update_session_status(session_id, 'failed')
            raise e
    
    async def process_batch_async(self, items: List[Dict], session_id: str = None, user_id: str = None):
        """Process a batch of items asynchronously"""
        session = None
        if session_id or user_id:
            session = db_manager.create_analysis_session({
                'session_name': f'AsyncBatch_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'user_id': user_id,
                'batch_size': len(items),
                'status': 'running'
            })
            session_id = session.id
        
        try:
            # Create tasks for all items
            tasks = [
                self._process_single_item_async(item, i)
                for i, item in enumerate(items)
            ]
            
            # Process all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'index': i,
                        'error': str(result),
                        'status': 'error'
                    })
                else:
                    result['index'] = i
                    processed_results.append(result)
                    
                    # Save to database if session exists
                    if session_id and result.get('classification'):
                        self._save_result_to_db(result, session_id)
            
            # Update session status
            if session:
                summary = self._generate_batch_summary(processed_results)
                db_manager.update_session_status(session_id, 'completed', summary)
            
            return {
                'results': processed_results,
                'summary': self._generate_batch_summary(processed_results),
                'session_id': session_id
            }
            
        except Exception as e:
            if session:
                db_manager.update_session_status(session_id, 'failed')
            raise e
    
    def _process_single_item(self, item: Dict, index: int) -> Dict:
        """Process a single item"""
        try:
            result = {
                'index': index,
                'input': item,
                'status': 'processing'
            }
            
            # Extract content
            content = None
            if 'url' in item:
                content = self.extractor.extract_from_url(item['url'])
                result['url'] = item['url']
                result['content_extracted'] = bool(content)
            elif 'text' in item:
                content = item['text']
                result['text_provided'] = True
            
            if not content:
                result['status'] = 'failed'
                result['error'] = 'No content available for classification'
                return result
            
            # Classify content
            classification = self.classifier.classify(content)
            if classification:
                result['classification'] = classification
                result['status'] = 'success'
            else:
                result['status'] = 'failed'
                result['error'] = 'Classification failed'
            
            return result
            
        except Exception as e:
            return {
                'index': index,
                'input': item,
                'status': 'error',
                'error': str(e)
            }
    
    async def _process_single_item_async(self, item: Dict, index: int) -> Dict:
        """Process a single item asynchronously"""
        async with self.semaphore:
            try:
                result = {
                    'index': index,
                    'input': item,
                    'status': 'processing'
                }
                
                # Extract content
                content = None
                if 'url' in item:
                    content = await self._extract_content_async(item['url'])
                    result['url'] = item['url']
                    result['content_extracted'] = bool(content)
                elif 'text' in item:
                    content = item['text']
                    result['text_provided'] = True
                
                if not content:
                    result['status'] = 'failed'
                    result['error'] = 'No content available for classification'
                    return result
                
                # Classify content (run in thread pool for CPU-bound task)
                loop = asyncio.get_event_loop()
                classification = await loop.run_in_executor(
                    None, self.classifier.classify, content
                )
                
                if classification:
                    result['classification'] = classification
                    result['status'] = 'success'
                else:
                    result['status'] = 'failed'
                    result['error'] = 'Classification failed'
                
                return result
                
            except Exception as e:
                return {
                    'index': index,
                    'input': item,
                    'status': 'error',
                    'error': str(e)
                }
    
    async def _extract_content_async(self, url: str) -> str:
        """Extract content from URL asynchronously"""
        try:
            timeout = aiohttp.ClientTimeout(total=Settings.REQUEST_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers={'User-Agent': Settings.USER_AGENT}) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self.extractor.clean_content(content)
                    else:
                        self.logger.warning(f"HTTP {response.status} for URL: {url}")
                        return None
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {str(e)}")
            return None
    
    def _save_result_to_db(self, result: Dict, session_id: str):
        """Save result to database"""
        try:
            if result.get('classification'):
                classification = result['classification']
                
                # Create or get company profile
                company_data = {
                    'company_name': result['input'].get('company_name', 'Unknown'),
                    'domain': self._extract_domain(result.get('url', '')),
                    'url': result.get('url', ''),
                    'primary_naics': classification.get('primary_naics'),
                    'confidence_score': classification.get('confidence', 0.0)
                }
                
                company = db_manager.create_company_profile(company_data)
                
                # Save classification result
                result_data = {
                    'company_id': company.id,
                    'session_id': session_id,
                    'primary_naics': classification.get('primary_naics'),
                    'secondary_naics': classification.get('secondary_naics', []),
                    'confidence_score': classification.get('confidence', 0.0),
                    'classification_method': classification.get('method', 'batch_ml'),
                    'extracted_keywords': classification.get('keywords', []),
                    'content_analysis': classification.get('analysis', {})
                }
                
                db_manager.save_classification_result(result_data)
                
        except Exception as e:
            self.logger.error(f"Error saving result to DB: {str(e)}")
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ''
    
    def _generate_batch_summary(self, results: List[Dict]) -> Dict:
        """Generate summary of batch processing results"""
        total = len(results)
        successful = len([r for r in results if r.get('status') == 'success'])
        failed = len([r for r in results if r.get('status') == 'failed'])
        errors = len([r for r in results if r.get('status') == 'error'])
        
        # Calculate average confidence for successful classifications
        successful_results = [r for r in results if r.get('status') == 'success' and r.get('classification')]
        avg_confidence = 0.0
        if successful_results:
            confidences = [r['classification'].get('confidence', 0.0) for r in successful_results]
            avg_confidence = sum(confidences) / len(confidences)
        
        # Count NAICS codes
        naics_counts = {}
        for result in successful_results:
            naics = result['classification'].get('primary_naics')
            if naics:
                naics_counts[naics] = naics_counts.get(naics, 0) + 1
        
        return {
            'total_items': total,
            'successful': successful,
            'failed': failed,
            'errors': errors,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'average_confidence': round(avg_confidence, 3),
            'top_naics_codes': dict(sorted(naics_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'processed_at': datetime.utcnow().isoformat()
        }

# Global instance
batch_processor = BatchProcessor()
