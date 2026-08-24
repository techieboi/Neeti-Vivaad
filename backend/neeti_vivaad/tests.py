import json
from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib import error

from django.test import SimpleTestCase, override_settings

from neeti_vivaad.ai import AIServiceError, generate_text, has_api_key


def successful_response(content="Generated response"):
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = json.dumps(
        {"choices": [{"message": {"content": content}}]}
    ).encode("utf-8")
    return response


class AIKeyFallbackTests(SimpleTestCase):
    @override_settings(NVIDIA_API_KEY="", NVIDIA_FALLBACK_API_KEY="fallback-key")
    @patch("neeti_vivaad.ai.request.urlopen")
    def test_uses_fallback_when_primary_key_is_missing(self, urlopen):
        urlopen.return_value = successful_response()

        self.assertTrue(has_api_key())
        self.assertEqual(generate_text("Prompt"), "Generated response")
        sent_request = urlopen.call_args.args[0]
        self.assertEqual(sent_request.get_header("Authorization"), "Bearer fallback-key")

    @override_settings(
        NVIDIA_API_KEY="primary-key",
        NVIDIA_FALLBACK_API_KEY="fallback-key",
    )
    @patch("neeti_vivaad.ai.request.urlopen")
    def test_retries_with_fallback_when_primary_is_rejected(self, urlopen):
        rejected = error.HTTPError(
            url="https://example.test/chat/completions",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=BytesIO(b'{"error":{"message":"Invalid API key"}}'),
        )
        urlopen.side_effect = [rejected, successful_response("Fallback response")]

        self.assertEqual(generate_text("Prompt"), "Fallback response")
        authorizations = [
            call.args[0].get_header("Authorization") for call in urlopen.call_args_list
        ]
        self.assertEqual(
            authorizations,
            ["Bearer primary-key", "Bearer fallback-key"],
        )

    @override_settings(
        NVIDIA_API_KEY="primary-key",
        NVIDIA_FALLBACK_API_KEY="fallback-key",
    )
    @patch("neeti_vivaad.ai.request.urlopen")
    def test_does_not_retry_non_key_server_errors(self, urlopen):
        urlopen.side_effect = error.HTTPError(
            url="https://example.test/chat/completions",
            code=500,
            msg="Server error",
            hdrs=None,
            fp=BytesIO(b'{"error":{"message":"Internal error"}}'),
        )

        with self.assertRaisesRegex(AIServiceError, r"failed \(500\): Internal error"):
            generate_text("Prompt")

        urlopen.assert_called_once()
