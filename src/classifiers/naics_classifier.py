import json
import re
import os
import openai
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
from urllib.parse import urlparse


class NAICSClassifier:
    """
    Ultra-robust NAICS classifier with:
      - Domain overrides
      - Pattern/keyword mapping
      - Semantic similarity
      - Zero-shot AI
      - OpenAI enrichment fallback
    """

    def __init__(self):
        self.naics_data: Dict[str, Dict] = {}
        self.naics_codes: List[str] = []
        self.naics_descriptions: List[str] = []
        self.classifier = None
        self.embedding_model = None
        self.industry_embeddings: Dict[str, np.ndarray] = {}

        self._load_naics_database()
        self._setup_classifier()
        self._setup_embeddings()
        self._build_industry_patterns()

    # -----------------------
    # Setup & Data Loading
    # -----------------------
    def _load_naics_database(self):
        base_path = Path(__file__).parent.parent.parent / "data" / "naics"
        for filename in ["comprehensive_naics_codes.json", "naics_codes.json"]:
            path = base_path / filename
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    self.naics_data = json.load(f)
                self.naics_codes = list(self.naics_data.keys())
                self.naics_descriptions = [
                    f"{v['title']}. {v['description']}"
                    for v in self.naics_data.values()
                ]
                print(f"✅ Loaded {len(self.naics_data)} NAICS industries from {filename}")
                return
        raise FileNotFoundError("No NAICS database found!")

    def _setup_classifier(self):
        try:
            from transformers import pipeline
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                return_all_scores=True
            )
            print("✅ Zero-shot classifier ready")
        except Exception as e:
            print(f"⚠️ Zero-shot unavailable: {e}")
            self.classifier = None

    def _setup_embeddings(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            important_codes = [
                "336111", "541511", "541430", "541810", "621111",
                "722511", "722515", "713940", "531210", "519130"
            ]
            for code in important_codes:
                if code in self.naics_data:
                    text = f"{self.naics_data[code]['title']}. {self.naics_data[code]['description']}"
                    self.industry_embeddings[code] = self.embedding_model.encode([text])[0]
            print(f"✅ Generated embeddings for {len(self.industry_embeddings)} industries")
        except Exception as e:
            print(f"⚠️ Semantic embeddings disabled: {e}")
            self.embedding_model = None
            self.industry_embeddings = {}

    def _build_industry_patterns(self):
        self.patterns = {
            "336111": ["tesla", "model s", "model 3", "model y", "cybertruck",
                       "automobile manufacturing", "electric vehicle", "ev"],
            "541511": ["wordpress", "software development", "app development", "custom software", "saas", "white label"],
            "541430": ["graphic design", "branding", "visual identity", "logo design"],
            "541810": ["marketing", "advertising", "seo", "social media"],
            "621111": ["medical practice", "physician", "primary care", "healthcare"],
            "722511": ["restaurant", "fine dining", "menu", "cuisine"],
            "722515": ["coffee shop", "cafe", "espresso", "latte"],
            "713940": ["fitness", "gym", "workout", "training"],
            "519130": ["social media platform", "internet publishing", "online community", "user profiles", "messaging"],
        }
        self.domain_overrides = {
            "tesla.com": "336111",
            "facebook.com": "519130",  # Internet Publishing & Broadcasting
            "google.com": "519130",
            "starbucks.com": "722515",
            "mcdonalds.com": "722513"
        }

    # -----------------------
    # Main Public Method
    # -----------------------
    def classify_business(self, content: Dict) -> Dict:
        domain = content.get("domain", "").lower()
        if not domain and "url" in content:
            parsed_url = urlparse(content["url"])
            domain = parsed_url.netloc.lower()

        text_blob = " ".join([
            content.get("title", ""),
            content.get("meta_description", ""),
            content.get("main_content", "")
        ]).lower()

        # 1️⃣ Domain override
        if domain in self.domain_overrides:
            return self._result(self.domain_overrides[domain], 0.95, "domain_override")

        # 2️⃣ Pattern matching
        pattern_result = self._pattern_match(text_blob)
        if pattern_result:
            return pattern_result

        # 3️⃣ Keyword category mapping
        cat_result = self._category_keywords(content)
        if cat_result:
            return cat_result

        # 4️⃣ Semantic similarity
        if self.embedding_model:
            sim_result = self._semantic_similarity(text_blob)
            if sim_result:
                return sim_result

        # 5️⃣ Zero-shot classification
        if self.classifier:
            zs_result = self._zero_shot(text_blob)
            if zs_result:
                return zs_result

        # 6️⃣ OpenAI enrichment
        enriched_text = self._external_api_lookup(domain)
        if enriched_text:
            return self.classify_business({
                "title": enriched_text,
                "main_content": enriched_text,
                "domain": domain
            })

        # 7️⃣ Default fallback
        return self._result("541511", 0.50, "default_fallback")

    # -----------------------
    # Classification Steps
    # -----------------------
    def _pattern_match(self, text: str) -> Optional[Dict]:
        for code, keywords in self.patterns.items():
            if any(kw in text for kw in keywords):
                count = sum(1 for kw in keywords if kw in text)
                conf = 0.90 if count > 1 else 0.80
                return self._result(code, conf, "pattern_match")
        return None

    def _category_keywords(self, content: Dict) -> Optional[Dict]:
        mapping = {
            "automotive": "336111",
            "technology": "541511",
            "design": "541430",
            "marketing": "541810",
            "healthcare": "621111",
            "food_service": "722511",
            "fitness": "713940",
            "retail": "445110",
            "internet": "519130"
        }
        bk = content.get("business_keywords", {})
        if not bk:
            return None
        cat, count = max(bk.items(), key=lambda x: x[1])
        if cat in mapping and count >= 2:
            return self._result(mapping[cat], min(0.85, 0.6 + 0.05 * count), "keyword_category")
        return None

    def _semantic_similarity(self, text: str) -> Optional[Dict]:
        if not text.strip():
            return None
        try:
            vec = self.embedding_model.encode([text])[0]
            sims = {}
            for code, emb in self.industry_embeddings.items():
                sim = float(np.dot(vec, emb) / (np.linalg.norm(vec) * np.linalg.norm(emb)))
                sims[code] = sim
            best_code, best_score = max(sims.items(), key=lambda x: x[1])
            if best_score > 0.70:
                return self._result(best_code, min(0.9, best_score + 0.05), "semantic_similarity")
        except Exception as e:
            print(f"⚠️ Semantic similarity failed: {e}")
        return None

    def _zero_shot(self, text: str) -> Optional[Dict]:
        if not text.strip():
            return None
        try:
            chunk_size = 40
            best_label, best_score = None, 0
            for i in range(0, len(self.naics_descriptions), chunk_size):
                chunk = self.naics_descriptions[i:i + chunk_size]
                res = self.classifier(text, chunk, multi_label=False)
                if res["scores"][0] > best_score:
                    best_score = res["scores"][0]
                    best_label = res["labels"][0]
            if best_label and best_score > 0.6:
                idx = self.naics_descriptions.index(best_label)
                code = self.naics_codes[idx]
                return self._result(code, best_score, "zero_shot")
        except Exception as e:
            print(f"⚠️ Zero-shot failed: {e}")
        return None

    # -----------------------
    # OpenAI Enrichment
    # -----------------------
    def _external_api_lookup(self, domain: str) -> Optional[str]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ No OpenAI API key found. Set OPENAI_API_KEY in environment.")
            return None
        openai.api_key = api_key
        try:
            prompt = f"Describe the primary business activities and industry of {domain} for NAICS classification."
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a business classification expert familiar with NAICS codes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0
            )
            enriched_text = response.choices[0].message.content.strip()
            print(f"🔍 OpenAI enrichment for {domain}: {enriched_text[:120]}...")
            return enriched_text
        except Exception as e:
            print(f"⚠️ OpenAI enrichment failed: {e}")
            return None

    # -----------------------
    # Result Formatting
    # -----------------------
    def _result(self, code: str, confidence: float, method: str) -> Dict:
        return {
            "predicted_naics_code": code,
            "predicted_industry": self.naics_data.get(code, {}).get("title", "Unknown"),
            "confidence_score": confidence,
            "classification_method": method,
            "fallback_category": self._fallback_category(code, confidence),
            "total_industries_considered": len(self.naics_data),
        }

    def _fallback_category(self, code: str, score: float) -> Optional[str]:
        if score >= 0.7:
            return None
        sector_map = {
            "33": "Manufacturing",
            "54": "Professional, Scientific, and Technical Services",
            "72": "Accommodation and Food Services",
            "62": "Health Care and Social Assistance",
            "44": "Retail Trade",
            "45": "Retail Trade",
            "51": "Information"
        }
        return sector_map.get(code[:2], "General Business Services")
