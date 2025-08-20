
class WebContentExtractor:
    def __init__(self):
        pass
        
    def extract_title(self, soup):
        if soup.title:
            return soup.title.string
        return None
        
    def extract_meta_description(self, soup):
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta['content'] if meta else None
        
    def extract_headers(self, soup):
        headers = []
        for tag in ['h1', 'h2', 'h3']:
            headers.extend([h.text for h in soup.find_all(tag)])
        return headers