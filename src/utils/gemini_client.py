"""Gemini API client for agent communication using google-genai SDK."""

import logging
from typing import Optional, Dict, Any
import google.genai as genai

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Client for interacting with Google Gemini API.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-1.5-pro-latest",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ):
        """
        Initialize Gemini client.
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize the client
        self.client = genai.Client(api_key=self.api_key)

        logger.info(f"GeminiClient initialized with model: {self.model_name}")

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate content using Gemini API.
        """
        try:
            # Use provided values or defaults
            temp = temperature if temperature is not None else self.temperature
            max_tok = max_tokens if max_tokens is not None else self.max_tokens

            # Build the full prompt with system instruction if provided
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"System: {system_instruction}\n\nUser: {prompt}"

            # Use the models.generate_content method
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temp,
                    max_output_tokens=max_tok
                )
            )

            # Extract text from response
            generated_text = response.text

            logger.debug(f"Generated response length: {len(generated_text)}")
            return generated_text

        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")

    def generate_with_context(
        self,
        prompt: str,
        context: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate content with additional context.
        """
        full_prompt = f"Context:\n{context}\n\nPrompt:\n{prompt}"
        return self.generate_content(
            prompt=full_prompt,
            system_instruction=system_instruction
        )

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        """
        # Rough estimation: ~4 characters per token
        return len(text) // 4

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost of API call.
        """
        input_cost = (input_tokens / 1000) * 0.00125
        output_cost = (output_tokens / 1000) * 0.00500
        return input_cost + output_cost

    def __repr__(self) -> str:
        """String representation of client."""
        return (
            f"GeminiClient(model={self.model_name}, "
            f"temperature={self.temperature}, "
            f"max_tokens={self.max_tokens})"
        )