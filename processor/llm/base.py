from abc import ABC, abstractmethod
from processor.models import Analysis


class LLMClient(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    def analyze(self, title: str, content: str, search_phrase: str) -> Analysis:
        """
        Analyze content for themes and sentiment.

        Args:
            title: The title of the content
            content: The body text to analyze
            search_phrase: The original search phrase for context

        Returns:
            Analysis object with themes, sentiment, summary, etc.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify the LLM service is reachable."""
        pass

    def build_analysis_prompt(self, title: str, content: str, search_phrase: str) -> str:
        """Build the analysis prompt."""
        return f"""Analyze the following content that was collected while searching for "{search_phrase}".

Title: {title}

Content:
{content}

Provide a structured analysis with:

1. THEMES: Identify 1-5 main themes. For each theme provide:
   - name: A short descriptive name (2-4 words)
   - confidence: How confident you are this theme is present (0.0-1.0)
   - keywords: 2-5 keywords associated with this theme

2. SENTIMENT: Classify the overall sentiment as one of:
   - very_negative, negative, neutral, positive, very_positive
   Also provide a sentiment_score from -1.0 (most negative) to 1.0 (most positive)

3. SUMMARY: A 1-2 sentence summary of the content

4. KEY_POINTS: 2-5 bullet points capturing the main takeaways

5. ENTITIES: List any people, organizations, or locations mentioned

Respond in JSON format:
{{
  "themes": [
    {{"name": "...", "confidence": 0.0, "keywords": ["...", "..."]}}
  ],
  "sentiment": "neutral",
  "sentiment_score": 0.0,
  "summary": "...",
  "key_points": ["...", "..."],
  "entities": ["...", "..."]
}}"""
