import json
from openai import OpenAI
from processor.llm.base import LLMClient
from processor.models import Analysis, Theme, Sentiment


class OpenAILLMClient(LLMClient):
    """OpenAI client for content analysis."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        max_tokens: int = 1024
    ):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def analyze(self, title: str, content: str, search_phrase: str) -> Analysis:
        prompt = self.build_analysis_prompt(title, content, search_phrase)

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        response_text = response.choices[0].message.content
        return self._parse_response(response_text)

    def _parse_response(self, response: str) -> Analysis:
        """Parse the JSON response into an Analysis object."""
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
            self.client.chat.completions.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception:
            return False
