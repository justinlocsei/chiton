import pytest

from chiton.core.encryption import decrypt, encrypt, rekey, EncryptionError


class TestDecrypt():

    def test_decrypt_encrypted(self):
        """It decrypts encrypted messages."""
        encrypted = encrypt('message')
        decrypted = decrypt(encrypted)

        assert decrypted == 'message'

    def test_decrypt_encoding(self):
        """It decrypts encoded messages as UTF-8 strings."""
        encrypted = encrypt('méssåge')
        decrypted = decrypt(encrypted)

        assert decrypted == 'méssåge'

    def test_decrypt_format(self):
        """It raises an error when trying to decrypt a non-encrypted value."""
        with pytest.raises(EncryptionError):
            decrypt('message')

    def test_decrypt_key(self):
        """It accepts a custom decryption key."""
        key = b'0' * 32

        encrypted = encrypt('message', key=key)
        assert decrypt(encrypted, key=key) == 'message'

    def test_decrypt_key_invalid(self):
        """It requires a 32-byte key."""
        encrypted = encrypt('message', key=b'0' * 32)

        with pytest.raises(EncryptionError):
            decrypt(encrypted, key=b'0' * 31)

    def test_decrypt_key_incorrect(self):
        """It raises an error when an incorrect key is provided."""
        right_key = b'0' * 32
        wrong_key = b'1' * 32

        encrypted = encrypt('message', key=right_key)

        with pytest.raises(EncryptionError):
            decrypt(encrypted, key=wrong_key)

    def test_decrypt_key_default(self, settings):
        """It gets its default key from settings."""
        settings.CHITON_ENCRYPTION_KEY = b'0' * 32

        encrypted = encrypt('message')
        assert decrypt(encrypted) == 'message'

        settings.CHITON_ENCRYPTION_KEY = b'1' * 32
        with pytest.raises(EncryptionError):
            decrypt(encrypted)


class TestEncrypt():

    def test_encrypt_encoding(self):
        """It encrypts messages as base64-encoded strings."""
        encrypted = encrypt('message')

        assert encrypted
        assert encrypted != 'message'
        assert type(encrypted) == str

    def test_encrypt_key(self):
        """It accepts a custom encryption key."""
        encrypted = encrypt('message', key=b'0' * 32)

        assert encrypted
        assert encrypted != 'message'

    def test_encrypt_key_invalid(self):
        """It requires a 32-byte key."""
        with pytest.raises(EncryptionError):
            encrypt('message', key=b'0' * 31)

    def test_encrypt_key_default(self, settings):
        """It gets its default key from settings."""
        settings.CHITON_ENCRYPTION_KEY = None

        with pytest.raises(EncryptionError):
            encrypt('message')

    def test_encrypt_nonce(self):
        """It does not produce the same message using the same key."""
        key = b'0' * 32
        message = 'message'

        assert encrypt(message, key=key) != encrypt(message, key=key)


class TestRekey():

    def test_rekey(self):
        """It re-encrypts an encrypted message using a new key."""
        old_key = b'0' * 32
        new_key = b'1' * 32

        old_encrypted = encrypt('message', key=old_key)
        new_encrypted = rekey(old_encrypted, old_key=old_key, new_key=new_key)

        assert decrypt(new_encrypted, key=new_key) == 'message'

    def test_rekey_non_encrypted(self):
        """It raises an error when trying to re-key a non-encrypted value."""
        with pytest.raises(EncryptionError):
            rekey('message', old_key=b'0' * 32, new_key=b'1' * 32)

    def test_rekey_key_format(self):
        """It raises an error when given an invalid new key."""
        old_key = b'0' * 32
        encrypted = encrypt('message', key=old_key)

        with pytest.raises(EncryptionError):
            rekey(encrypted, old_key=old_key, new_key=b'1' * 31)

    def test_rekey_defaults(self, settings):
        """It uses the settings for the default old and new key."""
        old_key = b'0' * 32
        new_key = b'1' * 32

        settings.CHITON_ENCRYPTION_KEY = new_key
        settings.CHITON_PREVIOUS_ENCRYPTION_KEY = old_key

        encrypted = encrypt('message', key=old_key)
        rekeyed = rekey(encrypted)

        assert decrypt(rekeyed) == 'message'
