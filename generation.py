"""Take the query + context and submits it to the LLM model."""

import os

import requests


class Generation:
    """Take the query + context and submits it to the LLM model."""

    def __init__(self, logger):
        self.logger = logger
        if os.environ.get("GENERATION_BACKEND") == "nvidia":
            self.model = os.environ.get("NVIDIA_MODEL")
            self.base_url = os.environ.get("NVIDIA_URL")
            self.key = os.environ.get("NVIDIA_API_KEY")
        elif os.environ.get("GENERATION_BACKEND") == "groq":
            self.model = os.environ.get("GROQ_MODEL")
            self.base_url = os.environ.get("GROQ_URL")
            self.key = os.environ.get("GROQ_API_KEY")
        else:
            raise ValueError(
                "Invalid GENERATION_BACKEND provided. Please set the GENERATION_BACKEND environment variable to either 'nvidia' or 'groq'."  # noqa: E501
            )

        if self.base_url is None:
            raise ValueError("Invalid base_url provided.")

        if self.model is None:
            raise ValueError("Invalid model provided.")

        if self.key is None:
            raise ValueError(
                "API key not found. Please set the GROQ_API_KEY or NVIDIA_API_KEY environment variable."  # noqa: E501
            )

    def generate(
        self,
        prompt: str,
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
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.key}"  # noqa: E501
                },
                json={
                    "model": self.model,
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
