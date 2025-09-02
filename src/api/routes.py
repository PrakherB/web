"""
Main API routes for NAICS classification
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.processors.main_processor import WebsiteAnalysisProcessor
from src.classifiers.naics_classifier import NAICSClassifier
from src.extractors.content_extractor import WebContentExtractor
from src.search.vector_search import find_similar_designs
from src.trends.main import collect_and_process_trends
from src.reporting.generator import ReportBuilder, ReportPromptGenerator
import logging
import traceback
import os

app = Flask(__name__)
CORS(app)

# Initialize components
processor = WebsiteAnalysisProcessor()
classifier = NAICSClassifier()
extractor = WebContentExtractor()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'timestamp': processor.get_timestamp()
    })

@app.route('/classify', methods=['POST'])
def classify_business():
    """Classify business based on URL or text"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not any(key in data for key in ['url', 'text']):
            return jsonify({
                'error': 'Missing required field: url or text'
            }), 400
        
        result = {}
        
        if 'url' in data:
            # Extract content from URL
            content = extractor.extract_from_url(data['url'])
            if not content:
                return jsonify({
                    'error': 'Failed to extract content from URL'
                }), 400
                
            # Classify content
            classification = classifier.classify(content)
            result = {
                'url': data['url'],
                'content_preview': content[:200] + '...' if len(content) > 200 else content,
                'classification': classification,
                'confidence': classification.get('confidence', 0),
                'primary_naics': classification.get('primary_naics'),
                'secondary_naics': classification.get('secondary_naics', [])
            }
        
        elif 'text' in data:
            # Classify provided text
            classification = classifier.classify(data['text'])
            result = {
                'text_preview': data['text'][:200] + '...' if len(data['text']) > 200 else data['text'],
                'classification': classification,
                'confidence': classification.get('confidence', 0),
                'primary_naics': classification.get('primary_naics'),
                'secondary_naics': classification.get('secondary_naics', [])
            }
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Classification error: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/batch_classify', methods=['POST'])
def batch_classify():
    """Batch classification endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'items' not in data:
            return jsonify({
                'error': 'Missing required field: items'
            }), 400
        
        items = data['items']
        if len(items) > 100:  # Limit batch size
            return jsonify({
                'error': 'Batch size too large. Maximum 100 items.'
            }), 400
        
        results = []
        for i, item in enumerate(items):
            try:
                if 'url' in item:
                    content = extractor.extract_from_url(item['url'])
                    classification = classifier.classify(content) if content else None
                elif 'text' in item:
                    classification = classifier.classify(item['text'])
                else:
                    classification = None
                
                results.append({
                    'index': i,
                    'classification': classification,
                    'status': 'success' if classification else 'failed'
                })
                
            except Exception as e:
                results.append({
                    'index': i,
                    'error': str(e),
                    'status': 'error'
                })
        
        return jsonify({
            'results': results,
            'total': len(items),
            'successful': len([r for r in results if r['status'] == 'success'])
        })
        
    except Exception as e:
        logging.error(f"Batch classification error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/naics/<code>', methods=['GET'])
def get_naics_info(code):
    """Get NAICS code information"""
    try:
        naics_info = classifier.get_naics_info(code)
        if not naics_info:
            return jsonify({
                'error': 'NAICS code not found'
            }), 404
            
        return jsonify(naics_info)
        
    except Exception as e:
        logging.error(f"NAICS info error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/v1/designs/search', methods=['POST'])
def search_designs():
    """
    Searches for similar designs based on a business description.
    """
    try:
        data = request.get_json()
        if not data or 'business_description' not in data:
            return jsonify({'error': 'Missing business_description'}), 400

        results = find_similar_designs(
            business_description=data['business_description'],
            naics_category=data.get('naics_category'),
            top_k=data.get('top_k', 10)
        )
        return jsonify(results)
    except Exception as e:
        logging.error(f"Design search error: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/v1/analyze', methods=['POST'])
def analyze_website():
    """
    Main endpoint to run a full analysis of a website.
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'Missing url'}), 400

        url = data['url']

        # 1. Extract content from URL
        content_data = extractor.extract_website_content(url)
        if not content_data or not content_data.get('main_content'):
            return jsonify({'error': 'Failed to extract sufficient content from URL'}), 400

        # 2. Classify business
        classification = classifier.classify_business(content_data)
        naics_code = classification.get('predicted_naics_code')
        industry_name = classification.get('predicted_industry')

        # 3. Find competitor designs (using vector search)
        competitors = find_similar_designs(
            business_description=content_data.get('meta_description') or content_data.get('title'),
            naics_category=naics_code,
            top_k=3
        )

        # 4. Fetch and analyze trends
        dribbble_api_key = os.getenv("DRIBBBLE_API_KEY")
        trends = collect_and_process_trends(feed_urls=[], dribbble_api_key=dribbble_api_key)

        # 5. Generate prompt for AI
        prompt_generator = ReportPromptGenerator()
        prompt_context = {
            "industry_name": industry_name,
            "business_description": content_data.get('meta_description') or content_data.get('title'),
            "naics_code": naics_code,
            "competitors": competitors.get('metadatas', [[]])[0],
            "trends": trends
        }
        prompt = prompt_generator.generate_prompt(**prompt_context)

        # 6. (Mocked) Get AI recommendations
        # In a real application, you would make an API call to an LLM here
        mock_recommendations = [
            {"suggestion": "Implement a minimalist design.", "priority_ranking": 1, "rationale": "To improve user focus.", "implementation_complexity": "Medium"},
            {"suggestion": "Use a sustainable design theme.", "priority_ranking": 2, "rationale": "To appeal to eco-conscious customers.", "implementation_complexity": "High"},
        ]

        # 7. Build the final report
        report_builder = ReportBuilder()
        report_data = {
            "classification_confidence": classification.get('confidence_score'),
            "naics_code": naics_code,
            "industry_description": industry_name,
            "competitors": competitors.get('metadatas', [[]])[0],
            "trends": trends,
            "custom_recommendations": mock_recommendations
        }
        report = report_builder.build(report_data)

        return jsonify(report.model_dump())

    except Exception as e:
        logging.error(f"Analysis error: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
