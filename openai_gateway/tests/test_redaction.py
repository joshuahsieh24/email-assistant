"""Unit tests for PII redaction functionality."""

import pytest
from app.redaction import PIIRedactor
from app.models import TokenMap


class TestPIIRedactor:
    """Test PII redaction functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.redactor = PIIRedactor()

    def test_redact_email(self):
        """Test redaction of email addresses."""
        text = "Contact me at john.doe@example.com for more information."
        redacted_text, token_mappings = self.redactor.redact_text(text)
        
        assert "john.doe@example.com" not in redacted_text
        assert "EMAIL" in redacted_text
        assert len(token_mappings) == 1
        assert token_mappings[0].original_text == "john.doe@example.com"
        assert token_mappings[0].entity_type == "EMAIL_ADDRESS"

    def test_redact_phone_number(self):
        """Test redaction of phone numbers."""
        text = "Call me at +1-555-123-4567 or (555) 987-6543"
        redacted_text, token_mappings = self.redactor.redact_text(text)
        
        assert "+1-555-123-4567" not in redacted_text
        assert "(555) 987-6543" not in redacted_text
        assert "PHONE" in redacted_text
        assert len(token_mappings) == 2

    def test_redact_person_name(self):
        """Test redaction of person names."""
        text = "John Smith and Jane Doe are working on this project."
        redacted_text, token_mappings = self.redactor.redact_text(text)
        
        assert "John Smith" not in redacted_text
        assert "Jane Doe" not in redacted_text
        assert "PERSON" in redacted_text
        assert len(token_mappings) == 2

    def test_redact_multiple_entities(self):
        """Test redaction of multiple entity types."""
        text = "Contact John Smith at john.smith@company.com or call +1-555-123-4567"
        redacted_text, token_mappings = self.redactor.redact_text(text)
        
        assert "John Smith" not in redacted_text
        assert "john.smith@company.com" not in redacted_text
        assert "+1-555-123-4567" not in redacted_text
        assert "PERSON" in redacted_text
        assert "EMAIL" in redacted_text
        assert "PHONE" in redacted_text
        assert len(token_mappings) == 3

    def test_redact_messages(self):
        """Test redaction of message lists."""
        messages = [
            {"role": "user", "content": "Contact John at john@example.com"},
            {"role": "assistant", "content": "I'll help you contact John."}
        ]
        
        redacted_messages, token_mappings = self.redactor.redact_messages(messages)
        
        assert len(redacted_messages) == 2
        assert redacted_messages[0]["role"] == "user"
        assert redacted_messages[1]["role"] == "assistant"
        assert "John" not in redacted_messages[0]["content"]
        assert "john@example.com" not in redacted_messages[0]["content"]
        assert len(token_mappings) == 2

    def test_no_pii_in_text(self):
        """Test handling of text with no PII."""
        text = "This is a simple message with no personal information."
        redacted_text, token_mappings = self.redactor.redact_text(text)
        
        assert redacted_text == text
        assert len(token_mappings) == 0

    def test_empty_text(self):
        """Test handling of empty text."""
        text = ""
        redacted_text, token_mappings = self.redactor.redact_text(text)
        
        assert redacted_text == text
        assert len(token_mappings) == 0

    def test_token_mapping_structure(self):
        """Test that token mappings have correct structure."""
        text = "Contact john@example.com"
        redacted_text, token_mappings = self.redactor.redact_text(text)
        
        assert len(token_mappings) == 1
        token_map = token_mappings[0]
        
        assert isinstance(token_map, TokenMap)
        assert token_map.original_text == "john@example.com"
        assert token_map.entity_type == "EMAIL_ADDRESS"
        assert isinstance(token_map.confidence, float)
        assert 0.0 <= token_map.confidence <= 1.0 