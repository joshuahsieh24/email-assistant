"""PII redaction using Microsoft Presidio."""

import uuid
from typing import Dict, List, Tuple

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from .models import TokenMap
from .settings import settings


class PIIRedactor:
    """PII redaction and re-identification using Presidio."""

    def __init__(self) -> None:
        """Initialize Presidio engines."""
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # Configure supported languages
        self.supported_languages = settings.presidio_supported_languages

    def redact_text(self, text: str, language: str = "en") -> Tuple[str, List[TokenMap]]:
        """
        Redact PII from text and return anonymized text with token mappings.
        
        Args:
            text: Input text to redact
            language: Language code for analysis
            
        Returns:
            Tuple of (anonymized_text, token_mappings)
        """
        if language not in self.supported_languages:
            language = "en"

        # Analyze text for PII
        analyzer_results = self.analyzer.analyze(
            text=text,
            language=language,
            entities=[
                "PERSON",
                "EMAIL_ADDRESS",
                "PHONE_NUMBER",
                "CREDIT_CARD",
                "IBAN_CODE",
                "IP_ADDRESS",
                "LOCATION",
                "DATE_TIME",
                "NRP",
                "MEDICAL_LICENSE",
                "US_SSN",
                "US_PASSPORT",
                "US_DRIVER_LICENSE",
                "CRYPTO",
                "UK_NHS",
            ],
        )

        # Configure anonymization operators
        operators = {
            "PERSON": OperatorConfig("replace", {"new_value": "PERSON"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "EMAIL"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "PHONE"}),
            "CREDIT_CARD": OperatorConfig("replace", {"new_value": "CREDIT_CARD"}),
            "IBAN_CODE": OperatorConfig("replace", {"new_value": "IBAN"}),
            "IP_ADDRESS": OperatorConfig("replace", {"new_value": "IP_ADDRESS"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "LOCATION"}),
            "DATE_TIME": OperatorConfig("replace", {"new_value": "DATE"}),
            "NRP": OperatorConfig("replace", {"new_value": "NRP"}),
            "MEDICAL_LICENSE": OperatorConfig("replace", {"new_value": "MEDICAL_LICENSE"}),
            "US_SSN": OperatorConfig("replace", {"new_value": "SSN"}),
            "US_PASSPORT": OperatorConfig("replace", {"new_value": "PASSPORT"}),
            "US_DRIVER_LICENSE": OperatorConfig("replace", {"new_value": "DRIVER_LICENSE"}),
            "CRYPTO": OperatorConfig("replace", {"new_value": "CRYPTO"}),
            "UK_NHS": OperatorConfig("replace", {"new_value": "NHS"}),
        }

        # Anonymize text
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators=operators,
        )

        # Create token mappings for re-identification
        token_mappings: List[TokenMap] = []
        
        for result in analyzer_results:
            token_id = f"TOKEN_{uuid.uuid4().hex[:8].upper()}"
            
            token_map = TokenMap(
                original_text=text[result.start:result.end],
                token_id=token_id,
                entity_type=result.entity_type,
                confidence=result.score,
            )
            token_mappings.append(token_map)

        return anonymized_result.text, token_mappings

    def redact_messages(self, messages: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[TokenMap]]:
        """
        Redact PII from a list of messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Tuple of (redacted_messages, all_token_mappings)
        """
        redacted_messages = []
        all_token_mappings: List[TokenMap] = []
        
        for message in messages:
            original_content = message["content"]
            redacted_content, token_mappings = self.redact_text(original_content)
            
            redacted_messages.append({
                "role": message["role"],
                "content": redacted_content,
            })
            
            all_token_mappings.extend(token_mappings)
        
        return redacted_messages, all_token_mappings


# Global redactor instance
redactor = PIIRedactor() 