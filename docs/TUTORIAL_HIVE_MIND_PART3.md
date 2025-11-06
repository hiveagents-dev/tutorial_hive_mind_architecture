# Tutorial: Implementing Hive Mind Architecture - Part III

**Continuation of TUTORIAL_HIVE_MIND_PART2.md**

---

# Part III: Practical Implementation (Continued)

## 14. Integration with LLMs (Gemini API)

### 14.1 LLM Client Design

**Design Goals**:
1. Abstract LLM provider (allow switching providers)
2. Retry logic for transient failures
3. Rate limiting compliance
4. Cost tracking
5. Prompt engineering best practices

```python
class GeminiClient:
    """
    Robust Gemini API client with enterprise features.

    Features:
    - Exponential backoff retry
    - Rate limiting
    - Token usage tracking
    - Error handling
    - Logging
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        max_retries: int = 3,
        timeout: int = 30
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.timeout = timeout

        # Initialize Gemini client
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

        # Metrics
        self.total_calls = 0
        self.total_tokens = 0
        self.total_cost = 0.0

        self.logger = logging.getLogger(__name__)

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate content with retry logic.

        Args:
            prompt: User prompt
            system_instruction: System context/role
            temperature: Override default temperature

        Returns:
            Generated text

        Raises:
            MaxRetriesExceeded: If all retries fail
            InvalidAPIKey: If authentication fails
        """
        temp = temperature if temperature is not None else self.temperature

        for attempt in range(self.max_retries):
            try:
                # Build generation config
                generation_config = {
                    "temperature": temp,
                    "max_output_tokens": self.max_tokens,
                }

                # Build full prompt
                full_prompt = self._build_full_prompt(
                    prompt,
                    system_instruction
                )

                # Call API
                self.logger.debug(f"Gemini API call (attempt {attempt + 1})")
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )

                # Extract text
                text = response.text

                # Update metrics
                self._update_metrics(response)

                return text

            except Exception as e:
                self._handle_exception(e, attempt)

        # All retries exhausted
        raise MaxRetriesExceeded(
            f"Failed after {self.max_retries} attempts"
        )

    def _build_full_prompt(
        self,
        prompt: str,
        system_instruction: Optional[str]
    ) -> str:
        """Combine system instruction and user prompt."""
        if system_instruction:
            return f"{system_instruction}\n\n---\n\n{prompt}"
        return prompt

    def _handle_exception(self, exception: Exception, attempt: int):
        """Handle different exception types with appropriate retry logic."""

        if attempt == self.max_retries - 1:
            # Last attempt, re-raise
            self.logger.error(f"Final attempt failed: {exception}")
            raise

        # Determine wait time based on exception type
        if isinstance(exception, RateLimitError):
            # Rate limit: longer wait
            wait_time = 10 * (2 ** attempt)
            self.logger.warning(
                f"Rate limited, waiting {wait_time}s before retry"
            )

        elif isinstance(exception, (NetworkError, TimeoutError)):
            # Network issue: exponential backoff
            wait_time = 2 ** attempt
            self.logger.warning(
                f"Network error, retrying in {wait_time}s: {exception}"
            )

        elif isinstance(exception, AuthenticationError):
            # Auth error: don't retry
            self.logger.error("Invalid API key")
            raise InvalidAPIKey("Check GEMINI_API_KEY environment variable")

        else:
            # Unknown error: exponential backoff
            wait_time = 2 ** attempt
            self.logger.warning(
                f"Unknown error, retrying in {wait_time}s: {exception}"
            )

        time.sleep(wait_time)

    def _update_metrics(self, response):
        """Track usage metrics."""
        self.total_calls += 1

        # Estimate tokens (Gemini doesn't always provide exact count)
        if hasattr(response, 'usage_metadata'):
            tokens = (
                response.usage_metadata.prompt_token_count +
                response.usage_metadata.candidates_token_count
            )
            self.total_tokens += tokens

            # Estimate cost (Gemini Flash: $0.002 per 1K tokens)
            cost = (tokens / 1000) * 0.002
            self.total_cost += cost

        self.logger.info(
            f"API call complete. "
            f"Total calls: {self.total_calls}, "
            f"Total cost: ${self.total_cost:.4f}"
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "avg_tokens_per_call": (
                self.total_tokens / self.total_calls
                if self.total_calls > 0 else 0
            ),
            "model": self.model_name
        }
```

### 14.2 Prompt Engineering Best Practices

```python
class PromptEngineer:
    """
    Best practices for prompt engineering.

    Based on:
    - OpenAI prompt engineering guide
    - Google Gemini best practices
    - Academic research on LLM prompting
    """

    @staticmethod
    def create_system_prompt(
        role: str,
        expertise: List[str],
        responsibilities: List[str],
        output_format: str,
        guidelines: List[str]
    ) -> str:
        """
        Create structured system prompt.

        Template follows proven structure:
        1. Role definition
        2. Expertise areas
        3. Responsibilities
        4. Output format
        5. Guidelines

        Returns:
            Well-structured system prompt
        """
        prompt_parts = [
            f"# Role: {role}",
            "",
            "## Expertise",
            "You are an expert in:",
        ]

        # Add expertise
        for item in expertise:
            prompt_parts.append(f"- {item}")

        prompt_parts.extend([
            "",
            "## Your Responsibilities",
        ])

        # Add responsibilities
        for i, resp in enumerate(responsibilities, 1):
            prompt_parts.append(f"{i}. {resp}")

        prompt_parts.extend([
            "",
            "## Output Format",
            output_format,
            "",
            "## Guidelines",
        ])

        # Add guidelines
        for guideline in guidelines:
            prompt_parts.append(f"- {guideline}")

        return "\n".join(prompt_parts)

    @staticmethod
    def add_few_shot_examples(
        prompt: str,
        examples: List[Tuple[str, str]]
    ) -> str:
        """
        Add few-shot examples to improve quality.

        Few-shot learning: Provide examples of desired input-output pairs

        Args:
            prompt: Base prompt
            examples: List of (input, output) tuples

        Returns:
            Enhanced prompt with examples
        """
        example_section = ["## Examples", ""]

        for i, (input_ex, output_ex) in enumerate(examples, 1):
            example_section.extend([
                f"### Example {i}",
                f"**Input:**",
                f"{input_ex}",
                "",
                f"**Output:**",
                f"{output_ex}",
                ""
            ])

        return prompt + "\n\n" + "\n".join(example_section)

    @staticmethod
    def add_chain_of_thought(prompt: str) -> str:
        """
        Encourage step-by-step reasoning (Chain of Thought).

        Research shows LLMs perform better when asked to
        "think step by step" (Wei et al., 2022)
        """
        cot_instruction = """
## Reasoning Process

Before providing your final answer, please:
1. **Analyze** the business need carefully
2. **Identify** key requirements and constraints
3. **Consider** multiple approaches
4. **Evaluate** trade-offs
5. **Formulate** your recommendation

Think through each step systematically.
"""
        return prompt + "\n" + cot_instruction

    @staticmethod
    def validate_prompt_length(
        prompt: str,
        max_tokens: int = 100000
    ) -> Tuple[bool, int]:
        """
        Validate prompt doesn't exceed token limits.

        Rough estimation: 1 token ≈ 4 characters
        """
        estimated_tokens = len(prompt) // 4

        is_valid = estimated_tokens < max_tokens

        return is_valid, estimated_tokens
```

### 14.3 LLM Response Parsing

```python
class ResponseParser:
    """Parse and validate LLM responses."""

    @staticmethod
    def extract_structured_content(
        response: str,
        expected_sections: List[str]
    ) -> Dict[str, str]:
        """
        Extract structured sections from markdown response.

        Example response:
        ## Business Case
        Content here...

        ## Stakeholder Map
        More content...

        Returns:
            {"Business Case": "Content here...", "Stakeholder Map": "More content..."}
        """
        sections = {}
        current_section = None
        current_content = []

        for line in response.split("\n"):
            # Check for section header
            if line.startswith("##"):
                # Save previous section
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                current_section = line.replace("#", "").strip()
                current_content = []

            elif current_section:
                current_content.append(line)

        # Save final section
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        # Validate expected sections present
        missing = set(expected_sections) - set(sections.keys())
        if missing:
            logger.warning(f"Missing expected sections: {missing}")

        return sections

    @staticmethod
    def extract_confidence_explicit(response: str) -> Optional[float]:
        """
        Extract explicit confidence if LLM provides it.

        Looks for patterns like:
        - "Confidence: 85%"
        - "Confidence Level: 0.85"
        - "I am 85% confident"
        """
        import re

        # Pattern 1: "Confidence: 85%"
        pattern1 = r"(?i)confidence:\s*(\d+)%"
        match = re.search(pattern1, response)
        if match:
            return float(match.group(1)) / 100

        # Pattern 2: "Confidence: 0.85"
        pattern2 = r"(?i)confidence:\s*([0-1]\.\d+)"
        match = re.search(pattern2, response)
        if match:
            return float(match.group(1))

        # Pattern 3: "85% confident"
        pattern3 = r"(\d+)%\s+confident"
        match = re.search(pattern3, response)
        if match:
            return float(match.group(1)) / 100

        return None

    @staticmethod
    def validate_response_quality(
        response: str,
        min_length: int = 500,
        required_keywords: Optional[List[str]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate response meets quality criteria.

        Returns:
            (is_valid, list_of_issues)
        """
        issues = []

        # Check length
        if len(response) < min_length:
            issues.append(
                f"Response too short: {len(response)} < {min_length} chars"
            )

        # Check for required keywords
        if required_keywords:
            response_lower = response.lower()
            missing_keywords = [
                kw for kw in required_keywords
                if kw.lower() not in response_lower
            ]
            if missing_keywords:
                issues.append(
                    f"Missing keywords: {', '.join(missing_keywords)}"
                )

        # Check for structure (headers)
        if "##" not in response:
            issues.append("No structured sections found (expected ##headers)")

        is_valid = len(issues) == 0

        return is_valid, issues
```

---

# Part IV: Advanced Topics

## 15. Testing Multi-Agent Systems

### 15.1 Testing Strategy

**Test Pyramid for Multi-Agent Systems**:

```
        /\
       /  \           E2E Tests (10%)
      /    \          - Full workflow tests
     /------\         - Real LLM calls
    /        \        - Expensive, slow
   /          \
  / Integration \     Integration Tests (30%)
 /              \     - Agent coordination
/__Unit_Tests___\    - Communication protocols
                      - Consensus mechanisms

                      Unit Tests (60%)
                      - Individual components
                      - Mocked LLM responses
                      - Fast, deterministic
```

### 15.2 Unit Testing Agents

```python
import pytest
from unittest.mock import Mock, MagicMock

class TestProductManagerAgent:
    """Unit tests for ProductManagerAgent."""

    @pytest.fixture
    def mock_gemini_client(self):
        """Mock Gemini client to avoid real API calls."""
        client = Mock(spec=GeminiClient)
        client.generate_content.return_value = """
        ## Business Case

        This is a high-value opportunity with strong market fit.

        ### Market Analysis
        - TAM: $500M
        - SAM: $100M
        - SOM: $10M

        ### Revenue Projection
        Year 1: $1M
        Year 2: $3M
        Year 3: $7M

        Confidence: 85%
        """
        return client

    @pytest.fixture
    def pm_agent(self, mock_gemini_client):
        """Create ProductManagerAgent with mocked client."""
        return ProductManagerAgent(
            gemini_client=mock_gemini_client,
            methodology=AgileMethodology.SCRUM
        )

    def test_agent_initialization(self, pm_agent):
        """Test agent initializes correctly."""
        assert pm_agent.name == "ProductManager"
        assert pm_agent.role == "Product Manager - Business Strategy & Market Analysis"
        assert pm_agent.methodology == AgileMethodology.SCRUM

    def test_system_prompt_contains_key_sections(self, pm_agent):
        """Test system prompt has required sections."""
        prompt = pm_agent.get_system_prompt()

        assert "Business Case" in prompt
        assert "Market Analysis" in prompt
        assert "Stakeholder Map" in prompt
        assert "ROI" in prompt

    def test_process_returns_structured_response(
        self,
        pm_agent,
        mock_gemini_client
    ):
        """Test process returns valid AgentResponse."""
        business_need = "Build a customer loyalty program"

        response = pm_agent.process(business_need)

        # Verify response structure
        assert isinstance(response, AgentResponse)
        assert response.agent_name == "ProductManager"
        assert 0.0 <= response.confidence <= 1.0
        assert len(response.content) > 0
        assert response.methodology == "scrum"

    def test_process_with_context(self, pm_agent, mock_gemini_client):
        """Test process incorporates context."""
        business_need = "Build app"
        context = {
            "methodology_context": "Scrum - Sprint-based delivery"
        }

        response = pm_agent.process(business_need, context=context)

        # Verify client was called with enriched prompt
        call_args = mock_gemini_client.generate_content.call_args
        prompt_used = call_args[1]['prompt']

        assert "Scrum" in prompt_used
        assert business_need in prompt_used

    def test_confidence_extraction(self, pm_agent):
        """Test confidence extraction from response."""
        # Response with explicit confidence
        response_text = "Analysis here... Confidence: 85%"
        confidence = pm_agent._extract_confidence(response_text)

        assert 0.8 <= confidence <= 0.9  # Should extract ~0.85

    def test_methodology_adaptation(self):
        """Test agent adapts to different methodologies."""
        mock_client = Mock(spec=GeminiClient)

        # Scrum agent
        scrum_agent = ProductManagerAgent(
            mock_client,
            methodology=AgileMethodology.SCRUM
        )
        scrum_prompt = scrum_agent.get_adapted_system_prompt()
        assert "Sprint" in scrum_prompt or "Scrum" in scrum_prompt

        # SAFe agent
        safe_agent = ProductManagerAgent(
            mock_client,
            methodology=AgileMethodology.SAFE
        )
        safe_prompt = safe_agent.get_adapted_system_prompt()
        assert "PI" in safe_prompt or "SAFe" in safe_prompt


class TestConsensusManager:
    """Unit tests for consensus mechanisms."""

    @pytest.fixture
    def sample_responses(self):
        """Sample agent responses for testing."""
        return [
            AgentResponse(
                agent_name="Agent1",
                content="Analysis 1",
                confidence=0.9
            ),
            AgentResponse(
                agent_name="Agent2",
                content="Analysis 2",
                confidence=0.85
            ),
            AgentResponse(
                agent_name="Agent3",
                content="Analysis 3",
                confidence=0.8
            ),
            AgentResponse(
                agent_name="Agent4",
                content="Analysis 4",
                confidence=0.75
            ),
            AgentResponse(
                agent_name="Agent5",
                content="Analysis 5",
                confidence=0.7
            ),
            AgentResponse(
                agent_name="Agent6",
                content="Analysis 6",
                confidence=0.65
            ),
        ]

    def test_weighted_voting_consensus(self, sample_responses):
        """Test weighted voting achieves consensus correctly."""
        manager = ConsensusManager()

        weights = {
            "Agent1": 1.5,
            "Agent2": 1.2,
            "Agent3": 1.0,
            "Agent4": 1.0,
            "Agent5": 0.8,
            "Agent6": 0.8
        }

        result = manager.apply_consensus(
            sample_responses,
            strategy=ConsensusStrategy.WEIGHTED_VOTING,
            context={"weights": weights}
        )

        assert isinstance(result, ConsensusResult)
        assert result.strategy_used == ConsensusStrategy.WEIGHTED_VOTING
        assert 0.0 <= result.consensus_level <= 1.0

        # High confidence agents weighted more → should achieve consensus
        assert result.achieved is True
        assert result.consensus_level > 0.75

    def test_majority_consensus(self, sample_responses):
        """Test majority consensus."""
        manager = ConsensusManager()

        result = manager.apply_consensus(
            sample_responses,
            strategy=ConsensusStrategy.MAJORITY
        )

        # 5 out of 6 agents have confidence >= 0.65 (threshold 0.6)
        # Majority = > 50% → should achieve consensus
        assert result.achieved is True

    def test_unanimous_consensus_not_achieved(self, sample_responses):
        """Test unanimous consensus fails with disagreement."""
        manager = ConsensusManager()

        result = manager.apply_consensus(
            sample_responses,
            strategy=ConsensusStrategy.UNANIMOUS
        )

        # One agent (0.65) below typical threshold (0.8)
        # Unanimous = ALL must agree → should NOT achieve
        assert result.achieved is False

    def test_empty_responses(self):
        """Test consensus with no responses."""
        manager = ConsensusManager()

        result = manager.apply_consensus(
            [],
            strategy=ConsensusStrategy.WEIGHTED_VOTING
        )

        assert result.achieved is False
        assert result.consensus_level == 0.0
```

### 15.3 Integration Testing

```python
class TestHiveMindIntegration:
    """Integration tests for full HiveMind workflow."""

    @pytest.fixture
    def hivemind_system(self):
        """Create HiveMind system with mocked LLM."""
        mock_client = create_mock_gemini_client()

        return HiveMindArchitecture(
            gemini_client=mock_client,
            methodology=AgileMethodology.SCRUM,
            consensus_strategy=ConsensusStrategy.WEIGHTED_VOTING
        )

    def test_full_workflow_execution(self, hivemind_system):
        """Test complete analysis workflow."""
        business_need = """
        Build a customer loyalty mobile app for retail chain.
        500 stores, 2M customers, target 60% repeat purchase rate.
        """

        result = hivemind_system.execute(
            business_need,
            verbose=False
        )

        # Verify result structure
        assert isinstance(result, HiveMindResult)
        assert len(result.worker_responses) == 6
        assert result.coordinator_response is not None
        assert result.supervisor_response is not None
        assert result.consensus_result is not None

        # Verify all workers executed
        agent_names = {r.agent_name for r in result.worker_responses}
        expected_agents = {
            "ProductManager",
            "ProductOwner",
            "UXUI_Designer",
            "TechnicalLead",
            "ScrumMaster",
            "QA_Specialist"
        }
        assert agent_names == expected_agents

        # Verify execution time recorded
        assert result.execution_time > 0

        # Verify metadata
        assert result.metadata["methodology"] == "scrum"
        assert result.metadata["total_agents"] == 8
        assert result.metadata["worker_count"] == 6

    def test_communication_logging(self, hivemind_system):
        """Test A2A communication is logged."""
        business_need = "Build an app"

        result = hivemind_system.execute(business_need, verbose=False)

        # Get communication statistics
        stats = hivemind_system.get_communication_statistics()

        assert stats["total_messages"] > 0
        assert "ProductManager" in stats["agents"]
        assert "Coordinator" in stats["agents"]
        assert "Supervisor" in stats["agents"]

        # Verify message types
        assert stats["message_types"]["request"] > 0
        assert stats["message_types"]["response"] > 0

    def test_consensus_achievement(self, hivemind_system):
        """Test consensus is properly achieved."""
        business_need = "Build an app"

        result = hivemind_system.execute(business_need, verbose=False)

        consensus = result.consensus_result

        # Verify consensus structure
        assert consensus.achieved in [True, False]
        assert 0.0 <= consensus.consensus_level <= 1.0
        assert len(consensus.justification) > 0
        assert consensus.strategy_used == ConsensusStrategy.WEIGHTED_VOTING


def create_mock_gemini_client():
    """Create mock Gemini client with realistic responses."""
    mock_client = Mock(spec=GeminiClient)

    def mock_generate(prompt, system_instruction=None, **kwargs):
        """Generate mock response based on agent type."""

        if "Product Manager" in system_instruction:
            return """
            ## Business Case
            High-value opportunity with strong ROI.

            Confidence: 89%
            """

        elif "Product Owner" in system_instruction:
            return """
            ## User Stories
            As a customer, I want to earn points...

            Confidence: 92%
            """

        # ... (similar for other agents)

        return "Generic analysis. Confidence: 85%"

    mock_client.generate_content.side_effect = mock_generate

    return mock_client
```

---

## 16. Observability and Monitoring

### 16.1 Logging Strategy

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """
    Structured JSON logging for observability.

    Why structured logging?
    - Machine-parseable (for log aggregation tools)
    - Rich context (add metadata)
    - Easy filtering/searching
    - Integration with observability platforms
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_json_formatter()

    def _setup_json_formatter(self):
        """Setup JSON formatter."""
        handler = logging.StreamHandler()

        # JSON formatter
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_execution_start(
        self,
        business_need: str,
        methodology: str
    ):
        """Log execution start with context."""
        self.logger.info(
            json.dumps({
                "event": "execution_start",
                "business_need_length": len(business_need),
                "methodology": methodology,
                "timestamp": datetime.now().isoformat()
            })
        )

    def log_agent_start(self, agent_name: str, phase: str):
        """Log agent execution start."""
        self.logger.info(
            json.dumps({
                "event": "agent_start",
                "agent": agent_name,
                "phase": phase
            })
        )

    def log_agent_complete(
        self,
        agent_name: str,
        confidence: float,
        execution_time: float
    ):
        """Log agent completion with metrics."""
        self.logger.info(
            json.dumps({
                "event": "agent_complete",
                "agent": agent_name,
                "confidence": confidence,
                "execution_time_ms": execution_time * 1000
            })
        )

    def log_consensus_result(
        self,
        strategy: str,
        achieved: bool,
        level: float
    ):
        """Log consensus result."""
        self.logger.info(
            json.dumps({
                "event": "consensus_result",
                "strategy": strategy,
                "achieved": achieved,
                "consensus_level": level
            })
        )
```

### 16.2 Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
executions_total = Counter(
    'hivemind_executions_total',
    'Total number of HiveMind executions',
    ['methodology', 'status']
)

execution_duration = Histogram(
    'hivemind_execution_duration_seconds',
    'HiveMind execution duration',
    ['methodology'],
    buckets=[10, 20, 30, 40, 50, 60, 80, 100, 120]
)

consensus_level = Histogram(
    'hivemind_consensus_level',
    'Consensus level achieved',
    ['strategy'],
    buckets=[0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
)

agent_confidence = Histogram(
    'hivemind_agent_confidence',
    'Individual agent confidence scores',
    ['agent_name'],
    buckets=[0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
)

llm_api_calls = Counter(
    'hivemind_llm_api_calls_total',
    'Total LLM API calls',
    ['status']
)

llm_cost = Counter(
    'hivemind_llm_cost_dollars',
    'Total LLM cost in dollars'
)


class MetricsCollector:
    """Collect and expose metrics."""

    @staticmethod
    def record_execution_start(methodology: str):
        """Record execution start."""
        executions_total.labels(
            methodology=methodology,
            status='started'
        ).inc()

    @staticmethod
    def record_execution_complete(
        methodology: str,
        duration: float,
        success: bool
    ):
        """Record execution completion."""
        status = 'success' if success else 'failure'

        executions_total.labels(
            methodology=methodology,
            status=status
        ).inc()

        if success:
            execution_duration.labels(
                methodology=methodology
            ).observe(duration)

    @staticmethod
    def record_consensus(strategy: str, level: float):
        """Record consensus result."""
        consensus_level.labels(strategy=strategy).observe(level)

    @staticmethod
    def record_agent_confidence(agent_name: str, confidence: float):
        """Record agent confidence."""
        agent_confidence.labels(agent_name=agent_name).observe(confidence)

    @staticmethod
    def record_llm_call(success: bool, cost: float):
        """Record LLM API call."""
        status = 'success' if success else 'failure'
        llm_api_calls.labels(status=status).inc()

        if success:
            llm_cost.inc(cost)
```

---

## 17. Scaling Hive Mind Systems

### 17.1 Horizontal Scaling Strategy

```python
"""
Scaling Dimensions:

1. Stateless Architecture
   - Each request independent
   - No session state in backend
   - Results persisted to database
   → Easy to add more instances

2. Load Balancing
   - Round-robin across instances
   - Health check endpoints
   - Sticky sessions NOT needed (stateless)

3. Database Scaling
   - Read replicas for analysis history
   - Connection pooling
   - Caching layer (Redis)

4. LLM Rate Limits
   - Multiple API keys (rotate)
   - Request queue with throttling
   - Batch processing for offline use cases
"""


class ScalableHiveMind:
    """Production-ready scalable HiveMind."""

    def __init__(
        self,
        gemini_clients: List[GeminiClient],  # Multiple API keys
        db_pool: DatabaseConnectionPool,
        cache: RedisCache,
        metrics: MetricsCollector
    ):
        self.gemini_clients = gemini_clients
        self.current_client_index = 0
        self.db_pool = db_pool
        self.cache = cache
        self.metrics = metrics

    def execute(self, business_need: str, **kwargs) -> HiveMindResult:
        """Execute with caching and load balancing."""

        # Check cache first
        cache_key = self._generate_cache_key(business_need, kwargs)
        cached_result = self.cache.get(cache_key)

        if cached_result:
            self.metrics.record_cache_hit()
            return cached_result

        # Get next available client (round-robin)
        client = self._get_next_client()

        # Create HiveMind with this client
        hivemind = HiveMindArchitecture(
            gemini_client=client,
            **kwargs
        )

        # Execute
        result = hivemind.execute(business_need)

        # Cache result (TTL: 1 hour)
        self.cache.set(cache_key, result, ttl=3600)

        # Persist to database (async)
        self._persist_async(result)

        return result

    def _get_next_client(self) -> GeminiClient:
        """Round-robin load balancing across API keys."""
        client = self.gemini_clients[self.current_client_index]
        self.current_client_index = (
            (self.current_client_index + 1) % len(self.gemini_clients)
        )
        return client

    def _generate_cache_key(
        self,
        business_need: str,
        kwargs: Dict
    ) -> str:
        """Generate cache key from inputs."""
        import hashlib

        # Include business need + methodology + consensus strategy
        cache_input = f"{business_need}|{kwargs.get('methodology', 'scrum')}|{kwargs.get('consensus_strategy', 'weighted')}"

        # Hash to fixed-length key
        return hashlib.sha256(cache_input.encode()).hexdigest()[:32]

    def _persist_async(self, result: HiveMindResult):
        """Persist result asynchronously to avoid blocking."""
        import threading

        def persist():
            try:
                db = self.db_pool.get_connection()
                db.save_analysis(result)
                db.close()
            except Exception as e:
                self.metrics.record_persistence_failure()
                logging.error(f"Persistence failed: {e}")

        thread = threading.Thread(target=persist)
        thread.start()
```

### 17.2 Performance Optimization

```python
class OptimizedHiveMind(HiveMindArchitecture):
    """HiveMind with performance optimizations."""

    async def execute_async(
        self,
        business_need: str,
        verbose: bool = True
    ) -> HiveMindResult:
        """
        Async execution with parallel worker processing.

        Optimization: Workers are independent → can run in parallel
        Expected speedup: 30-35 seconds (from 50 seconds sequential)
        """
        import asyncio

        start_time = time.time()
        result = HiveMindResult()

        # Phase 1: Workers in PARALLEL
        if verbose:
            print("[PHASE 1: Worker Agents - Parallel Execution]")

        worker_tasks = [
            self._execute_worker_async(worker, business_need, verbose)
            for worker in self.worker_agents
        ]

        result.worker_responses = await asyncio.gather(*worker_tasks)

        # Phase 2: Coordinator (sequential - needs all worker outputs)
        if verbose:
            print("\n[PHASE 2: Coordinator Synthesis]")

        result.coordinator_response = await self._execute_coordinator_async(
            business_need,
            result.worker_responses,
            verbose
        )

        # Phase 3: Supervisor (sequential - needs coordinator output)
        if verbose:
            print("\n[PHASE 3: Supervisor - Final Requirements]")

        result.supervisor_response = await self._execute_supervisor_async(
            business_need,
            result.coordinator_response,
            verbose
        )

        result.execution_time = time.time() - start_time

        return result

    async def _execute_worker_async(
        self,
        worker: BaseAgent,
        business_need: str,
        verbose: bool
    ) -> AgentResponse:
        """Execute single worker asynchronously."""
        if verbose:
            print(f"  → {worker.name}: Processing...", end="", flush=True)

        # Wrap synchronous agent in async
        response = await asyncio.to_thread(
            worker.process,
            business_need
        )

        if verbose:
            print(f" ✓ ({response.confidence:.2f})")

        return response
```

---

**[Continue to Part V: Exercises and Labs...]**

Would you like me to continue with Part V (Exercises, Labs, Case Studies, and References)?
