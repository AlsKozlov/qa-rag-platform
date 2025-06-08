import unittest
from unittest.mock import patch
from app.service import run_inference

class TestRunInference(unittest.TestCase):
    @patch('app.service.pipeline')
    def test_run_inference_success(self, mock_pipeline):
        mock_pipeline.return_value = [
            {"generated_text": ["Hello, world!"]}
        ]

        result = run_inference(
            system_msg="You are a helpful assistant.",
            user_msg="Hello!",
            temperature=0.7,
            top_p=0.9,
            max_tokens=50
        )
        self.assertEqual(result, "Hello, world!")

    @patch('app.service.pipeline')
    def test_run_inference_empty_output(self, mock_pipeline):
        mock_pipeline.return_value = [
            {"generated_text": [""]}
        ]
        result = run_inference(
            system_msg="You are a helpful assistant.",
            user_msg="Hello!",
            temperature=0.7,
            top_p=0.9,
            max_tokens=50
        )
        self.assertEqual(result, "")
