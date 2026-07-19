import unittest

from src.auth.utils import create_access_token, decode_token


class TokenTests(unittest.TestCase):
    def test_create_access_token_includes_refresh_jti(self):
        token = create_access_token(
            {"email": "user@example.com"},
            refresh=False,
            refresh_jti="refresh-123",
        )
        token_data = decode_token(token)

        self.assertEqual(token_data["refresh_jti"], "refresh-123")


if __name__ == "__main__":
    unittest.main()
