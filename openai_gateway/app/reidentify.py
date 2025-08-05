"""PII re-identification from tokens back to original text."""

import json
from typing import Dict, List

from .models import TokenMap


class PIIReidentifier:
    """Re-identify PII tokens back to original text."""

    def __init__(self) -> None:
        """Initialize re-identifier."""
        pass

    def reidentify_text(self, text: str, token_mappings: List[TokenMap]) -> str:
        """
        Replace tokens in text with original PII values.
        
        Args:
            text: Text containing tokens to replace
            token_mappings: List of token mappings
            
        Returns:
            Text with tokens replaced by original values
        """
        reidentified_text = text
        
        # Create a mapping from token_id to original_text
        token_map = {mapping.token_id: mapping.original_text for mapping in token_mappings}
        
        # Replace all tokens with original values
        for token_id, original_text in token_map.items():
            reidentified_text = reidentified_text.replace(token_id, original_text)
        
        return reidentified_text

    def reidentify_messages(self, messages: List[Dict[str, str]], token_mappings: List[TokenMap]) -> List[Dict[str, str]]:
        """
        Re-identify PII tokens in a list of messages.
        
        Args:
            messages: List of message dictionaries
            token_mappings: List of token mappings
            
        Returns:
            List of messages with tokens replaced
        """
        reidentified_messages = []
        
        for message in messages:
            reidentified_content = self.reidentify_text(message["content"], token_mappings)
            
            reidentified_messages.append({
                "role": message["role"],
                "content": reidentified_content,
            })
        
        return reidentified_messages

    def reidentify_openai_response(self, response: Dict, token_mappings: List[TokenMap]) -> Dict:
        """
        Re-identify PII tokens in OpenAI response.
        
        Args:
            response: OpenAI API response dictionary
            token_mappings: List of token mappings
            
        Returns:
            Response with tokens replaced
        """
        reidentified_response = response.copy()
        
        # Re-identify content in choices
        if "choices" in reidentified_response:
            for choice in reidentified_response["choices"]:
                if "message" in choice and "content" in choice["message"]:
                    choice["message"]["content"] = self.reidentify_text(
                        choice["message"]["content"], token_mappings
                    )
        
        return reidentified_response


# Global reidentifier instance
reidentifier = PIIReidentifier() 