import logging
from typing import Optional, Tuple

from ai.ia_prompt_integration import IAIntegration

logger = logging.getLogger(__name__)


class IAClient:
    """Wrapper around IAIntegration to centralize error handling."""

    def __init__(self, ia_instance: IAIntegration):
        self._ia = ia_instance

    def call(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            reasoning, response = self._ia.fetch_response(prompt)
            return reasoning, response
        except Exception as e:
            logger.exception("IA call failed: %s", e)
            return ("No reasoning due to error: " + str(e), "No response due to error: " + str(e))
