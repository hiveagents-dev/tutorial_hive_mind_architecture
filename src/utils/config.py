"""Configuration management for HiveMind system."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """
    Configuration class for managing environment variables and system settings.

    This class centralizes all configuration parameters for the HiveMind system,
    including API keys, model settings, and logging configuration.
    """

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro-latest")
        self.temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
        self.max_tokens: int = int(os.getenv("MAX_TOKENS", "2048"))
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

        # Validate configuration
        self._validate()

        # Setup logging
        self._setup_logging()

    def _validate(self) -> None:
        """
        Validate required configuration parameters.

        Raises:
            ValueError: If required configuration is missing or invalid.
        """
        if not self.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is required. "
                "Please set it in your .env file or environment variables."
            )

        if self.temperature < 0 or self.temperature > 2:
            raise ValueError(f"TEMPERATURE must be between 0 and 2, got {self.temperature}")

        if self.max_tokens < 1:
            raise ValueError(f"MAX_TOKENS must be positive, got {self.max_tokens}")

    def _setup_logging(self) -> None:
        """Configure logging for the application."""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format=log_format
        )

    def get_api_key(self) -> str:
        """
        Get Google API key.

        Returns:
            str: The configured Google API key.
        """
        return self.google_api_key

    def get_model_config(self) -> dict:
        """
        Get model configuration parameters.

        Returns:
            dict: Dictionary containing model name, temperature, and max tokens.
        """
        return {
            "model": self.gemini_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

    def __repr__(self) -> str:
        """String representation of configuration (hiding API key)."""
        return (
            f"Config(model={self.gemini_model}, "
            f"temperature={self.temperature}, "
            f"max_tokens={self.max_tokens}, "
            f"log_level={self.log_level})"
        )
