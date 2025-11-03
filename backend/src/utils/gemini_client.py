"""Gemini API client for agent communication using google-genai SDK."""

import logging
from typing import Optional, Dict, Any
import google.genai as genai
import time
import random

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
        max_tokens: int = 8192
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
        max_tokens: Optional[int] = None,
        response_mime_type: Optional[str] = None,
        model_name: Optional[str] = None,
        max_retries: int = 3
    ) -> str:
        """
        Generate content using Gemini API with rate limiting and retry logic.
        """
        for attempt in range(max_retries):
            try:
                # Use provided values or defaults
                temp = temperature if temperature is not None else self.temperature
                max_tok = max_tokens if max_tokens is not None else self.max_tokens
                mdl = model_name if model_name else self.model_name

                # Build the full prompt with system instruction if provided
                full_prompt = prompt
                if system_instruction:
                    full_prompt = f"System: {system_instruction}\n\nUser: {prompt}"

                # Use the models.generate_content method
                response = self.client.models.generate_content(
                    model=mdl,
                    contents=full_prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=temp,
                        max_output_tokens=max_tok,
                        response_mime_type=response_mime_type if response_mime_type else None
                    )
                )

                # Extract text from response
                generated_text = response.text

                logger.debug(f"Generated response length: {len(generated_text)}")
                return generated_text

            except Exception as e:
                error_str = str(e)
                logger.warning(f"Attempt {attempt + 1} failed: {error_str}")
                
                # Check if it's a rate limit error
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        # Extract retry delay from error if available
                        retry_delay = self._extract_retry_delay(error_str)
                        if retry_delay:
                            logger.info(f"Rate limit hit, waiting {retry_delay} seconds...")
                            time.sleep(retry_delay)
                        else:
                            # Exponential backoff with jitter
                            base_delay = (2 ** attempt) * 10  # 10s, 20s, 40s
                            jitter = random.uniform(0.5, 1.5)
                            delay = base_delay * jitter
                            logger.info(f"Rate limit hit, waiting {delay:.1f} seconds...")
                            time.sleep(delay)
                        continue
                    else:
                        logger.error(f"All retry attempts exhausted for rate limit")
                        raise Exception(f"Gemini API rate limit exceeded after {max_retries} attempts")
                else:
                    # Non-rate-limit error, don't retry
                    logger.error(f"Error generating content: {error_str}")
                    raise Exception(f"Gemini API error: {error_str}")
        
        # This should never be reached, but just in case
        raise Exception("Unexpected error in generate_content")
    
    def _extract_retry_delay(self, error_str: str) -> Optional[float]:
        """Extract retry delay from error message if available."""
        try:
            # Look for "retry in Xs" pattern
            import re
            match = re.search(r'retry in (\d+(?:\.\d+)?)s', error_str, re.IGNORECASE)
            if match:
                return float(match.group(1))
        except Exception:
            pass
        return None

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