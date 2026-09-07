from unittest.mock import Mock, patch

import pytest

from generation import Generation


def test_generate_returns_model_content():
    fake_response = Mock()
    fake_response.json.return_value = {
        "choices": [{"message": {"content": "the answer"}}]
    }
    with patch("generation.requests.post", return_value=fake_response) as mock_post:
        result = Generation().generate("some prompt")

    assert result == "the answer"
    mock_post.assert_called_once()


def test_generate_raises_on_empty_prompt():
    with pytest.raises(ValueError):
        Generation().generate("")
