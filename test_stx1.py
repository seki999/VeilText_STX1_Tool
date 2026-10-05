import base64
import json
import unittest

from veiltext_stx1_recovery import (
    AAD,
    ITERATIONS,
    NONCE_LENGTH,
    SALT_LENGTH,
    TAG_LENGTH,
    decrypt_veiltext,
    encrypt_veiltext,
)


class STX1CompatibilityTests(unittest.TestCase):
    def test_unicode_round_trip(self):
        plaintext = "中文测试\n日本語テスト\nEnglish test\nEmoji: 🔐"
        password = "Test-Password-123!"

        encrypted = encrypt_veiltext(plaintext, password)
        recovered = decrypt_veiltext(encrypted, password)

        self.assertEqual(recovered, plaintext)

    def test_generated_payload_matches_stx1_v1_shape(self):
        encrypted = encrypt_veiltext("hello", "password")
        self.assertTrue(encrypted.startswith("STX1:"))

        payload = json.loads(
            base64.b64decode(encrypted[5:], validate=True).decode("utf-8")
        )

        self.assertEqual(payload["Version"], 1)
        self.assertEqual(payload["Algorithm"], "AES-256-GCM")
        self.assertEqual(payload["Kdf"], "PBKDF2-SHA256")
        self.assertEqual(payload["Iterations"], ITERATIONS)
        self.assertEqual(len(base64.b64decode(payload["Salt"], validate=True)), SALT_LENGTH)
        self.assertEqual(len(base64.b64decode(payload["Nonce"], validate=True)), NONCE_LENGTH)
        self.assertEqual(len(base64.b64decode(payload["Tag"], validate=True)), TAG_LENGTH)
        self.assertGreater(len(base64.b64decode(payload["Ciphertext"], validate=True)), 0)
        self.assertEqual(AAD, b"STX1|AES-256-GCM|PBKDF2-SHA256|600000")

    def test_same_plaintext_and_password_produce_different_ciphertexts(self):
        first = encrypt_veiltext("same text", "same password")
        second = encrypt_veiltext("same text", "same password")

        self.assertNotEqual(first, second)
        self.assertEqual(decrypt_veiltext(first, "same password"), "same text")
        self.assertEqual(decrypt_veiltext(second, "same password"), "same text")

    def test_wrong_password_fails(self):
        encrypted = encrypt_veiltext("secret", "correct password")

        with self.assertRaises(ValueError):
            decrypt_veiltext(encrypted, "wrong password")

    def test_empty_plaintext_is_rejected(self):
        with self.assertRaises(ValueError):
            encrypt_veiltext("", "password")

    def test_empty_password_is_rejected_for_new_encryption(self):
        with self.assertRaises(ValueError):
            encrypt_veiltext("secret", "")


if __name__ == "__main__":
    unittest.main()
