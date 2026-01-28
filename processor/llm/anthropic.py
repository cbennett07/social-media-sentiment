import json
import anthropic
from processor.llm.base import LLMClient
from processor.models import Analysis, Theme, Sentiment


class AnthropicLLMClient(LLMClient):
    """Anthropic Claude client for content analysis."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 1024
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def analyze(self, title: str, content: str, search_phrase: str) -> Analysis:
        prompt = self.build_analysis_prompt(title, content, search_phrase)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text
        return self._parse_response(response_text)

    def _parse_response(self, response: str) -> Analysis:
        """Parse the JSON response into an Analysis object."""
        # Handle potential markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]

        data = json.loads(response.strip())

        themes = [
            Theme(
                name=t["name"],
                confidence=float(t["confidence"]),
                keywords=t.get("keywords", [])
            )
            for t in data.get("themes", [])
        ]

        return Analysis(
            themes=themes,
            sentiment=Sentiment(data["sentiment"]),
            sentiment_score=float(data["sentiment_score"]),
            summary=data["summary"],
            key_points=data.get("key_points", []),
            entities=data.get("entities", []),
        )

    def health_check(self) -> bool:
        try:
            # Simple completion to verify API access
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception:
            return False
