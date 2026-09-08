"""Take the query + context and submits it to the LLM model."""

import os

import requests


class Generation:
    """Take the query + context and submits it to the LLM model."""

    def __init__(self, logger):
        self.logger = logger

    def generate(
        self,
        prompt: str,
        model: str = "openai/gpt-oss-120b",
        base_url: str = "https://api.groq.com/openai/v1",
        request_id: str = None,
    ) -> str:
        """Send the prompt + context to the model and return the result."""
        if not prompt:
            raise ValueError("No prompt provided to generate.")

        self.logger.info(
            "QUERY SENT TO MODEL",
            extra={"context": {"request_id": str(request_id), "prompt": prompt}},
        )
        try:
            result = requests.post(
                f"{base_url}/chat/completions",
                headers={
                    # "Authorization": f"Bearer {TEST_KEY}"  # noqa: E501
                    "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"  # noqa: E501
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60,
            )
        except requests.exceptions.Timeout:
            self.logger.error(
                "Request to LLM model timed out.",
                extra={"context": {"request_id": str(request_id)}},
            )
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(
                f"Error occurred while sending request: {e}",
                extra={"context": {"request_id": str(request_id)}},
            )
            return None
        try:
            json_result = result.json()
        except requests.exceptions.JSONDecodeError as e:
            self.logger.error(
                f"Error decoding JSON response: {e}",
                extra={"context": {"request_id": str(request_id)}},
            )
            return None
        try:
            self.logger.info(
                f"QUERY COMPLETED --- STATUS CODE {result.status_code}",
                extra={"context": {"request_id": str(request_id)}},
            )
            response_message = json_result["choices"][0]["message"]["content"]
            self.logger.info(
                "RESPONSE",
                extra={
                    "context": {
                        "request_id": str(request_id),
                        "response": response_message,
                    }
                },
            )
            self.logger.info(
                "TOKEN USAGE:",
                extra={
                    "context": {
                        "request_id": str(request_id),
                        "prompt_tokens": json_result["usage"]["prompt_tokens"],
                        "completion_tokens": json_result["usage"]["completion_tokens"],
                        "total_tokens": json_result["usage"]["total_tokens"],
                    }
                },
            )
        except KeyError as e:
            self.logger.error(
                f"Error accessing expected keys in JSON response: {e}",
                extra={"context": {"request_id": str(request_id)}},
            )
            return None

        return response_message
