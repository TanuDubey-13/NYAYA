import os
import json
from typing import List, Optional, Dict, Any
from app.schemas.models import KnowledgeSource, Jurisdiction

class KnowledgeRepository:
    """Manages the ingestion and lookup of official legal and civic documents."""
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.sources: List[KnowledgeSource] = []
        self.load_sources()

    def load_sources(self) -> List[KnowledgeSource]:
        """Loads and parses the curated corpus from the filesystem."""
        if not os.path.exists(self.data_path):
            self.sources = []
            return self.sources

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                sources_data = data.get("sources", [])
                
                self.sources = []
                for src in sources_data:
                    juris_data = src.get("jurisdiction", {})
                    jurisdiction = Jurisdiction(
                        country=juris_data.get("country", "India"),
                        state=juris_data.get("state", ""),
                        city=juris_data.get("city", ""),
                        localityOrWard=juris_data.get("localityOrWard", "")
                    )
                    
                    source = KnowledgeSource(
                        sourceId=src.get("sourceId"),
                        title=src.get("title"),
                        authority=src.get("authority"),
                        jurisdiction=jurisdiction,
                        category=src.get("category"),
                        subcategory=src.get("subcategory", "general"),
                        officialUrl=src.get("officialUrl"),
                        content=src.get("content"),
                        lastVerified=src.get("lastVerified"),
                        tags=src.get("tags", [])
                    )
                    self.sources.append(source)
        except Exception as e:
            print(f"Error loading corpus: {e}")
            self.sources = []
            
        return self.sources

    def get_source_by_id(self, source_id: str) -> Optional[KnowledgeSource]:
        """Retrieves a single source by its unique ID."""
        for src in self.sources:
            if src.sourceId == source_id:
                return src
        return None

    def list_sources(self) -> List[KnowledgeSource]:
        """Lists all loaded sources."""
        return self.sources

    def filter_sources(
        self, 
        country: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[KnowledgeSource]:
        """Filters resources by jurisdiction values and category tags."""
        filtered = self.sources
        
        if country:
            filtered = [s for s in filtered if s.jurisdiction.country.lower() == country.lower()]
        if state:
            filtered = [s for s in filtered if s.jurisdiction.state.lower() == state.lower()]
        if city:
            filtered = [s for s in filtered if s.jurisdiction.city.lower() == city.lower()]
        if category:
            filtered = [s for s in filtered if s.category.lower() == category.lower()]
            
        return filtered

class Retriever:
    """
    Retrieves relevant documentation chunks matching user queries.
    Decouples business logic from vector or keyword algorithms.
    """
    # Common English stop-words to prevent false positive matches
    STOP_WORDS = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", 
        "yours", "he", "him", "his", "she", "her", "it", "its", "they", "them", 
        "their", "what", "which", "who", "whom", "this", "that", "these", "those", 
        "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", 
        "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", 
        "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", 
        "for", "with", "about", "against", "between", "into", "through", "during", 
        "before", "after", "above", "below", "to", "from", "up", "down", "in", 
        "out", "on", "off", "over", "under", "again", "further", "then", "once", 
        "here", "there", "when", "where", "why", "how", "all", "any", "both", 
        "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", 
        "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", 
        "just", "don", "should", "now", "need", "needs", "help", "want", "wants", 
        "please", "regarding", "issue", "problem", "there", "has", "been", "for"
    }

    def __init__(self, repository: KnowledgeRepository):
        self.repository = repository

    def retrieve(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieves matching sources using a structured scoring system.
        Weights semantic overlap, category alignment, and hard jurisdiction boundaries.
        """
        sources = self.repository.list_sources()
        results = []
        
        # Parse filter parameters
        filter_country = filters.get("country") if filters else None
        filter_state = filters.get("state") if filters else None
        filter_city = filters.get("city") if filters else None
        filter_category = filters.get("category") if filters else None
        filter_subcategory = filters.get("subcategory") if filters else None

        # Extract search terms and filter out stop-words
        raw_words = query.lower().replace(",", "").replace(".", "").replace("?", "").replace("!", "").split()
        query_words = {w for w in raw_words if w not in self.STOP_WORDS}
        
        for src in sources:
            # 1. Semantic Similarity (Word overlap ratio)
            content_words = set(src.content.lower().replace(",", "").replace(".", "").split())
            title_words = set(src.title.lower().replace(",", "").replace(".", "").split())
            
            overlap_content = len(query_words.intersection(content_words))
            overlap_title = len(query_words.intersection(title_words))
            
            semantic_score = 0.0
            if query_words:
                semantic_score = (overlap_content * 0.5 + overlap_title * 1.0) / len(query_words)

            # 2. Category Match & Mismatch
            category_score = 0.0
            if filter_category:
                if src.category.lower() == filter_category.lower():
                    category_score += 2.0  # Category match bonus
                else:
                    category_score -= 5.0  # Category mismatch penalty

            # 3. Subcategory Match
            subcategory_score = 0.0
            if filter_subcategory:
                if src.subcategory.lower() == filter_subcategory.lower():
                    subcategory_score += 3.0  # Subcategory match bonus
                else:
                    subcategory_score -= 1.0  # Small penalty for subcategory mismatch

            # 4. Jurisdiction Matching
            jurisdiction_score = 0.0
            state_mismatch = False
            city_mismatch = False
            
            src_state = src.jurisdiction.state.lower() if src.jurisdiction.state else ""
            src_city = src.jurisdiction.city.lower() if src.jurisdiction.city else ""
            
            if filter_state and src_state and src_state != "national":
                if filter_state.lower() != src_state:
                    state_mismatch = True
                    
            if filter_city and src_city:
                if filter_city.lower() != src_city:
                    city_mismatch = True

            if state_mismatch or city_mismatch:
                continue  # Hard filter out sources from the wrong jurisdiction
            
            # Jurisdiction matches or is national fallback
            if filter_state and src_state == filter_state.lower():
                if filter_city and src_city == filter_city.lower():
                    jurisdiction_score += 2.0  # Exact City + State match
                else:
                    jurisdiction_score += 1.0  # State match
            elif src_state == "national" or src_state == "":
                jurisdiction_score += 0.5  # National fallback match

            # 5. Tag Match Bonus
            tag_score = 0.0
            matching_tags = 0
            for tag in src.tags:
                if tag.lower() in query.lower():
                    matching_tags += 1
            tag_score = matching_tags * 0.5

            # If there is absolutely no semantic overlap and no tag match, skip this source
            if semantic_score == 0.0 and tag_score == 0.0:
                continue

            # Calculate final score
            final_score = semantic_score + category_score + subcategory_score + jurisdiction_score + tag_score
            
            # Print developer log for validation during hackathon
            print(f"[RAG DEBUG] Source: {src.sourceId} ({src.title}) | "
                  f"Semantic: {semantic_score:.2f} | Category: {category_score:.2f} | "
                  f"Subcategory: {subcategory_score:.2f} | Jurisdiction: {jurisdiction_score:.2f} | "
                  f"Tags: {tag_score:.2f} | Final Score: {final_score:.2f}")

            results.append({
                "sourceId": src.sourceId,
                "chunkId": f"{src.sourceId}_c1",
                "text": src.content,
                "similarityScore": final_score,
                "authority": src.authority,
                "jurisdiction": {
                    "country": src.jurisdiction.country,
                    "state": src.jurisdiction.state,
                    "city": src.jurisdiction.city,
                    "localityOrWard": src.jurisdiction.localityOrWard
                },
                "officialUrl": src.officialUrl,
                "metadata": {"tags": src.tags, "category": src.category, "subcategory": src.subcategory}
            })
            
        # Sort results by similarityScore descending
        results.sort(key=lambda x: x["similarityScore"], reverse=True)
        return results
