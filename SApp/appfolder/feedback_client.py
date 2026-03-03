from openai import OpenAI

class FeedbackClient:
    def __init__(self):
        self.client = OpenAI(api_key="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")

    def get_personalized_feedback(self, scores):
        prompt = f"""
You are an elite 10m air pistol coach.

Analyze these scores:
{scores}

Give:
1. Technical correction advice
2. Mental performance advice
3. One specific drill for next practice
Keep it concise and professional.
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional Olympic shooting coach."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content
    