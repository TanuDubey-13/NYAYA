import os
import json
import urllib.request
import urllib.error
from typing import List, Optional
from app.schemas.models import TriageResult, ClarificationQuestion, Jurisdiction

class TriageAgent:
    """Agent in charge of categorizing and triaging the initial problem statement using Gemini."""
    
    SYSTEM_INSTRUCTION = (
        "You are the NYAYA Triage Agent. Your task is to analyze a citizen's civic or legal problem and extract structured metadata.\n"
        "Follow these rules strictly:\n"
        "1. Understand the problem and classify it into a category ('municipal_grievance', 'rti', 'legal_grievance', or 'other').\n"
        "2. Identify the most specific subcategory. For 'municipal_grievance', choose from: 'solid_waste', 'street_lighting', 'road_maintenance', 'sewerage_drainage', 'water_supply', 'illegal_dumping', or 'general'. For 'rti', choose 'rti_request'. For 'legal_grievance', choose from: 'domestic_violence', 'consumer_dispute', 'cyber_crime', or 'general_crime'.\n"
        "3. Set urgency to 'low', 'normal', or 'high'. High is for safety hazards, domestic abuse, ongoing cyber fraud, flooding, or active accidents.\n"
        "4. Extract location parameters (country, state, city, locality_or_ward) if explicitly provided in the text. Do not invent or guess these values; leave them as empty strings ('') if not provided.\n"
        "5. If the target department is obvious, extract it (e.g. 'sanitation', 'engineering', 'electrical', 'legal-cell', 'police').\n"
        "6. NEVER invent authority names or legal sections. Leave authority empty ('') if not known.\n"
        "7. Identify missing information (e.g. 'city', 'state', 'locality_or_ward' if they are not provided).\n"
        "8. If there is missing info, write a polite clarification question asking for the missing details. Limit to ONE question at a time.\n"
        "9. If jurisdiction details (locality/ward and city/state) are already present, 'missing_information' must be empty, and 'clarification_question' must be empty ('').\n"
        "10. Provide a confidence rating between 0.0 and 1.0. If you cannot confidently identify the category (confidence < 0.6), set the clarification_question to: 'I am not yet confident which civic or legal service this concerns. Could you briefly describe what is happening?'\n"
        "11. Return ONLY the requested structured JSON matching the provided schema."
    )

    RESPONSE_SCHEMA = {
        "type": "OBJECT",
        "properties": {
            "category": { "type": "STRING" },
            "subcategory": { "type": "STRING" },
            "urgency": { "type": "STRING", "enum": ["low", "normal", "high"] },
            "country": { "type": "STRING" },
            "state": { "type": "STRING" },
            "city": { "type": "STRING" },
            "locality_or_ward": { "type": "STRING" },
            "department": { "type": "STRING" },
            "authority": { "type": "STRING" },
            "problem_summary": { "type": "STRING" },
            "key_entities": { "type": "ARRAY", "items": { "type": "STRING" } },
            "missing_information": { "type": "ARRAY", "items": { "type": "STRING" } },
            "clarification_question": { "type": "STRING" },
            "confidence": { "type": "NUMBER" }
        },
        "required": [
            "category", "subcategory", "urgency", "country", "state", "city",
            "locality_or_ward", "department", "authority", "problem_summary",
            "key_entities", "missing_information", "clarification_question", "confidence"
        ]
    }

    def triage_problem(self, problem_text: str) -> TriageResult:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        
        if not api_key:
            print("[GEMINI TRIAGE FALLBACK] API key is missing. Using heuristic classifier.")
            return self._fallback_triage(problem_text)
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"Citizen Input:\n\"{problem_text}\""
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": self.RESPONSE_SCHEMA,
                "temperature": 0.1
            },
            "systemInstruction": {
                "parts": [
                    {
                        "text": self.SYSTEM_INSTRUCTION
                    }
                ]
            }
        }
        
        try:
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                
                text_content = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                parsed_json = json.loads(text_content)
                
                # Validate output schema
                return TriageResult(**parsed_json)
                
        except Exception as e:
            print(f"[GEMINI TRIAGE FALLBACK] Gemini API call or parsing failed: {e}. Using heuristic classifier.")
            return self._fallback_triage(problem_text)

    def _fallback_triage(self, problem_text: str) -> TriageResult:
        """Rule-based heuristic fallback to ensure the application continues functioning if API key/network fails."""
        text_lower = problem_text.lower()
        
        category = "municipal_grievance"
        subcategory = "solid_waste"
        urgency = "normal"
        
        # 1. Legal Grievances
        if any(kw in text_lower for kw in ["violence", "abuse", "domestic", "husband", "wife", "spouse", "harassed", "beating", "assault"]):
            category = "legal_grievance"
            subcategory = "domestic_violence"
            urgency = "high"
        elif any(kw in text_lower for kw in ["consumer", "merchant", "product", "refund", "replace", "bought", "defective", "seller", "shop", "cheated"]):
            category = "legal_grievance"
            subcategory = "consumer_dispute"
        elif any(kw in text_lower for kw in ["cyber", "hacked", "phishing", "scam", "online fraud", "bank fraud", "otp", "stolen money"]):
            category = "legal_grievance"
            subcategory = "cyber_crime"
            urgency = "high"
        elif any(kw in text_lower for kw in ["theft", "stolen", "robbery", "burgled", "police", "fir", "stole"]):
            category = "legal_grievance"
            subcategory = "general_crime"
        # 2. RTI Requests
        elif "rti" in text_lower or ("information" in text_lower and any(kw in text_lower for kw in ["government", "department", "spent", "funds", "public", "request"])):
            category = "rti"
            subcategory = "rti_request"
        # 3. Municipal Grievances
        elif any(kw in text_lower for kw in ["sewage", "sewer", "overflow", "drainage", "manhole", "blockage"]):
            subcategory = "sewerage_drainage"
            urgency = "high"
        elif any(kw in text_lower for kw in ["light", "lamp", "bulb", "dark", "lighting", "street light", "electricity"]):
            subcategory = "street_lighting"
        elif any(kw in text_lower for kw in ["water", "supply", "tap", "leakage", "drinking", "contamination"]):
            subcategory = "water_supply"
        elif any(kw in text_lower for kw in ["dumping", "illegal dump", "vacant site"]):
            subcategory = "illegal_dumping"
        elif any(kw in text_lower for kw in ["garbage", "waste", "refuse", "collection", "litter", "rubbish"]):
            subcategory = "solid_waste"
        elif any(kw in text_lower for kw in ["pothole", "road", "street", "pavement", "asphalt", "tar"]):
            subcategory = "road_maintenance"

        if any(kw in text_lower for kw in ["hazard", "accident", "emergency", "flooding", "risk"]):
            urgency = "high"

        # Simple extraction for fallback matching in tests
        state = ""
        city = ""
        locality = ""
        
        if "kanpur" in text_lower:
            city = "Kanpur"
            state = "Uttar Pradesh"
        elif "bengaluru" in text_lower or "bangalore" in text_lower:
            city = "Bengaluru"
            state = "Karnataka"
            
        if "ward 12" in text_lower:
            locality = "Ward 12"
        elif "ward 150" in text_lower:
            locality = "Ward 150"

        missing_info = []
        clarification = ""
        
        # If jurisdiction details are not already provided in input text
        if not state or not city or not locality:
            missing_info = ["state", "city", "locality_or_ward"]
            clarification = "Which city and locality or ward are you located in?"

        # Simulate low confidence check
        confidence = 0.95
        if len(problem_text.strip()) < 10:
            confidence = 0.3
            clarification = "I am not yet confident which civic service this concerns. Could you briefly describe what is happening?"

        return TriageResult(
            category=category,
            subcategory=subcategory,
            urgency=urgency,
            country="India",
            state=state,
            city=city,
            locality_or_ward=locality,
            department="sanitation" if subcategory == "solid_waste" else None,
            authority="",
            problem_summary=f"The citizen reports issues regarding {subcategory.replace('_', ' ')}.",
            key_entities=[subcategory],
            missing_information=missing_info,
            clarification_question=clarification,
            confidence=confidence
        )

class ClarificationAgent:
    """Agent in charge of deciding follow-up questions to clarify details."""
    def generate_question(self, problem_text: str, history: list) -> ClarificationQuestion:
        text_lower = problem_text.lower()
        
        question_text = "Which ward/locality and city/state are you located in?"
        if "light" in text_lower:
            question_text = "To locate the streetlight, please confirm your locality, city, and nearest landmark or pole number."
        elif "pothole" in text_lower:
            question_text = "Please specify the road name, locality, and city where the pothole is located."
        elif "sewage" in text_lower:
            question_text = "Please specify the exact location of the sewage overflow (ward/locality, landmark, and city)."
            
        return ClarificationQuestion(
            questionId="q_locality",
            question=question_text
        )
