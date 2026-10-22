import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from credentials import load_douyin_cookie, load_tiktok_cookie_header


class CredentialLoadingTests(unittest.TestCase):
    def test_douyin_environment_value_takes_precedence(self):
        with patch.dict(os.environ, {'DOUYIN_COOKIE': 'test-cookie'}, clear=True):
            self.assertEqual(load_douyin_cookie('missing.txt'), 'test-cookie')

    def test_tiktok_cookie_file_converts_json_to_header(self):
        with tempfile.TemporaryDirectory() as directory:
            cookie_file = Path(directory) / 'cookies.json'
            cookie_file.write_text('{"first": "one", "second": "two"}', encoding='utf-8')

            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(
                    load_tiktok_cookie_header(str(cookie_file)),
                    'first=one; second=two',
                )
