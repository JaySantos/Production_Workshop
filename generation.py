"""Take the query + context and submits it to the LLM model."""

import os

import requests


class Generation:
    """Take the query + context and submits it to the LLM model."""

    def generate(
        self,
        prompt: str,
        model: str = "openai/gpt-oss-120b",
        base_url: str = "https://api.groq.com/openai/v1",
    ) -> str:
        """Send the prompt + context to the model and return the result."""
        if not prompt:
            raise ValueError("No prompt provided to generate.")

        result = requests.post(
            f"{base_url}/chat/completions",
            headers={
                # "Authorization": f"Bearer {TEST_KEY}"  # noqa: E501
                "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"  # noqa: E501
            },
            json={"model": model, "messages": [{"role": "user", "content": prompt}]},
            timeout=60,
        )
        print(result.status_code)
        print(result.json())
        print(result.json()["choices"][0]["message"]["content"])
        return result.json()["choices"][0]["message"]["content"]
