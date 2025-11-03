"""Base agent class for HiveMind architecture."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from pydantic import BaseModel, Field

from utils.gemini_client import GeminiClient
from hivemind.methodology import AgileMethodology, MethodologyAdapter

logger = logging.getLogger(__name__)


class AgentResponse(BaseModel):
    """
    Structured response from an agent.

    Attributes:
        agent_name: Name/role of the agent.
        content: Main response content.
        confidence: Confidence score (0.0 to 1.0).
        metadata: Additional metadata about the response.
        timestamp: When the response was generated.
        methodology: Agile methodology used.
        methodology_specific_output: Output adapted to methodology.
    """
    agent_name: str
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    methodology: Optional[str] = None
    methodology_specific_output: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the HiveMind system.

    This class defines the common interface and functionality that all agents
    (Workers, Coordinators, and Supervisors) must implement.

    Attributes:
        name: Agent's name or identifier.
        role: Agent's role description.
        gemini_client: Client for interacting with Gemini API.
    """

    def __init__(
        self,
        name: str,
        role: str,
        gemini_client: GeminiClient,
        methodology: Optional[AgileMethodology] = None
    ):
        """
        Initialize base agent.

        Args:
            name: Unique name for the agent.
            role: Description of agent's role.
            gemini_client: Initialized Gemini client.
            methodology: Agile methodology to adapt to.
        """
        self.name = name
        self.role = role
        self.gemini_client = gemini_client
        self.methodology = methodology
        self.methodology_adapter = MethodologyAdapter(methodology) if methodology else None
        self.logger = logging.getLogger(f"{__name__}.{name}")

        methodology_info = f" with {methodology.value}" if methodology else ""
        self.logger.info(f"Agent '{name}' initialized with role: {role}{methodology_info}")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        This defines the agent's expertise, perspective, and instructions.

        Returns:
            str: System prompt text.
        """
        pass
    
    def get_adapted_system_prompt(self) -> str:
        """
        Get the system prompt adapted to the selected methodology.

        Returns:
            str: Adapted system prompt text.
        """
        base_prompt = self.get_system_prompt()
        
        if self.methodology_adapter:
            return self.methodology_adapter.adapt_system_prompt(base_prompt, self.name)
        
        return base_prompt

    @abstractmethod
    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process input and generate response.

        Args:
            input_data: Input data to process.
            context: Optional contextual information.

        Returns:
            AgentResponse: Structured response from the agent.
        """
        pass

    def _call_gemini(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Make a call to Gemini API.

        Args:
            prompt: Input prompt.
            system_instruction: Optional system instruction.
            temperature: Optional temperature override.

        Returns:
            str: Generated response.

        Raises:
            Exception: If API call fails.
        """
        try:
            self.logger.debug(f"Calling Gemini API with prompt length: {len(prompt)}")

            response = self.gemini_client.generate_content(
                prompt=prompt,
                system_instruction=system_instruction or self.get_adapted_system_prompt(),
                temperature=temperature
            )

            self.logger.debug(f"Received response length: {len(response)}")
            return response

        except Exception as e:
            self.logger.error(f"Error calling Gemini API: {str(e)}")
            raise

    def _extract_confidence(self, response_text: str) -> float:
        """
        Extract confidence score from response text.

        This is a simple heuristic. Subclasses can override for more
        sophisticated extraction.

        Args:
            response_text: Response text to analyze.

        Returns:
            float: Confidence score between 0.0 and 1.0.
        """
        # Simple heuristic: longer, more detailed responses = higher confidence
        # Real implementation would use NLP or explicit confidence markers
        length_score = min(len(response_text) / 1000, 1.0)
        return max(0.5, length_score)  # Minimum confidence of 0.5

    def communicate(self, message: str, recipient: 'BaseAgent') -> str:
        """
        Send a message to another agent.

        Args:
            message: Message content.
            recipient: Recipient agent.

        Returns:
            str: Response from recipient agent.
        """
        self.logger.info(f"Agent '{self.name}' communicating with '{recipient.name}'")

        # In a full implementation, this would use the A2A protocol
        # For now, it's a simple method call
        response = recipient.process(message)
        return response.content

    def get_info(self) -> Dict[str, str]:
        """
        Get agent information.

        Returns:
            dict: Agent metadata.
        """
        return {
            "name": self.name,
            "role": self.role,
            "type": self.__class__.__name__,
            "methodology": self.methodology.value if self.methodology else None
        }
    
    def _create_response(
        self,
        content: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Create an AgentResponse with methodology-specific adaptations.

        Args:
            content: Response content.
            confidence: Confidence score.
            metadata: Additional metadata.

        Returns:
            AgentResponse: Structured response.
        """
        if metadata is None:
            metadata = {}
        
        # Add methodology-specific metadata
        metadata.update({
            "role": self.role,
            "methodology": self.methodology.value if self.methodology else None
        })
        
        # Get methodology-specific output format
        methodology_output = None
        if self.methodology_adapter:
            methodology_output = self.methodology_adapter.adapt_output_format(self.name)
        
        return AgentResponse(
            agent_name=self.name,
            content=content,
            confidence=confidence,
            metadata=metadata,
            methodology=self.methodology.value if self.methodology else None,
            methodology_specific_output=methodology_output
        )

    def __repr__(self) -> str:
        """String representation of agent."""
        return f"{self.__class__.__name__}(name='{self.name}', role='{self.role}')"
