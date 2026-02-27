"""Base agent class for LifeOS AI agents."""
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from anthropic import Anthropic

from config import get_settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all LifeOS agents."""

    def __init__(self, name: str):
        """
        Initialize base agent.

        Args:
            name: Agent name
        """
        self.name = name
        self.settings = get_settings()
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize AI client based on configured provider."""
        if self.settings.ai_provider == "anthropic":
            if not self.settings.anthropic_api_key:
                logger.warning("Anthropic API key not configured")
                return

            self.client = Anthropic(api_key=self.settings.anthropic_api_key)
            logger.info(f"Initialized {self.name} with Claude")

        elif self.settings.ai_provider == "openai":
            if not self.settings.openai_api_key:
                logger.warning("OpenAI API key not configured")
                return

            # OpenAI client initialization would go here
            logger.info(f"Initialized {self.name} with OpenAI")

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and return results.

        Args:
            input_data: Input data for processing

        Returns:
            Processing results
        """
        pass

    async def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
    ) -> str:
        """
        Call the LLM with a prompt.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            max_tokens: Maximum tokens to generate

        Returns:
            LLM response text
        """
        if not self.client:
            logger.error("AI client not initialized")
            return ""

        try:
            if self.settings.ai_provider == "anthropic":
                message = self.client.messages.create(
                    model=self.settings.claude_model,
                    max_tokens=max_tokens,
                    system=system_prompt if system_prompt else "",
                    messages=[{"role": "user", "content": prompt}],
                )
                return message.content[0].text

            elif self.settings.ai_provider == "openai":
                # OpenAI implementation would go here
                pass

        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return ""

    def log_action(
        self,
        action: str,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        success: bool = True,
        error: Optional[str] = None,
        execution_time: Optional[float] = None,
    ):
        """
        Log agent action.

        Args:
            action: Action description
            input_data: Input data
            output_data: Output data
            success: Success flag
            error: Error message if failed
            execution_time: Execution time in seconds
        """
        log_entry = {
            "agent_name": self.name,
            "action": action,
            "input_data": input_data,
            "output_data": output_data,
            "success": success,
            "error_message": error,
            "execution_time": execution_time,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if success:
            logger.info(f"{self.name}: {action} - SUCCESS")
        else:
            logger.error(f"{self.name}: {action} - FAILED: {error}")

        # TODO: Store in database
        return log_entry
