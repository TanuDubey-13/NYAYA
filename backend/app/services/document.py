import os
import json
from typing import Dict, Any, Optional
from app.schemas.models import DraftDocument

class DocumentGeneratorService:
    """Manages legal application/grievance drafts and jurisdiction templates."""
    def __init__(self, templates_path: str):
        self.templates_path = templates_path
        self.templates: Dict[str, Any] = {}
        self.load_templates()

    def load_templates(self):
        """Loads seeded templates from templates.json."""
        if not os.path.exists(self.templates_path):
            self.templates = {}
            return
        
        try:
            with open(self.templates_path, "r", encoding="utf-8") as f:
                self.templates = json.load(f)
        except Exception as e:
            print(f"Error loading templates: {e}")
            self.templates = {}

    def get_template(self, doc_type: str) -> Optional[Dict[str, Any]]:
        """Fetches template schema by type (grievance, rti, general)."""
        return self.templates.get(doc_type)

    def generate_draft(self, doc_type: str, user_inputs: Dict[str, Any]) -> DraftDocument:
        """
        Populates standard placeholders using user inputs.
        Missing fields remain as explicit [ENTER INFORMATION] values.
        """
        template_info = self.get_template(doc_type)
        if not template_info:
            return DraftDocument(
                docType="general",
                title="General Civic Draft",
                content="[ENTER SUBJECT]\n\n[ENTER DETAILS]"
            )

        title = template_info.get("title", f"Draft {doc_type.upper()}")
        body_template = template_info.get("body", "")

        # Safe dictionary interpolation
        filled_body = body_template
        placeholders = template_info.get("placeholders", [])
        
        for ph in placeholders:
            val = user_inputs.get(ph)
            placeholder_tag = f"[ENTER {ph.upper()}]"
            if val:
                filled_body = filled_body.replace(placeholder_tag, str(val))
            # Else remains as default placeholder e.g. [ENTER NAME]

        # Add mandatory AI disclaimer to generated draft
        filled_body += "\n\n---\n*Disclaimer: AI-generated draft — review before submission.*"

        return DraftDocument(
            docType=doc_type,
            title=title,
            content=filled_body
        )
