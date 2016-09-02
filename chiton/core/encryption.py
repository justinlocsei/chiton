from base64 import b64decode, b64encode
import binascii
from django.conf import settings
from nacl.exceptions import CryptoError
from nacl.secret import SecretBox
import nacl.utils


MESSAGE_ENCODING = 'utf-8'
OUTPUT_ENCODING = 'ascii'


class EncryptionError(Exception):
    """An error indicating issues during encryption or decryption."""


def encrypt(message, key=None):
    """Encrypt a message.

    Args:
        message (str): A message to encrypt

    Keyword Args:
        key (bytes): The secret key to use

    Returns:
        str: The encrypted message encoded in base64

    Raises:
        chiton.core.encryption.EncryptionError: If the key is invalid
    """
    box = _create_secret_box(key)
    nonce = nacl.utils.random(SecretBox.NONCE_SIZE)

    message_bytes = message.encode(MESSAGE_ENCODING)
    encrypted_bytes = box.encrypt(message_bytes, nonce)

    return b64encode(encrypted_bytes).decode(OUTPUT_ENCODING)


def decrypt(value, key=None):
    """Decrypt a message.

    Args:
        message (str): A message to decrypt

    Keyword Args:
        key (bytes): The secret key to use

    Returns:
        str: The decrypted message

    Raises:
        chiton.core.encryption.EncryptionError: If the key is invalid
    """
    box = _create_secret_box(key)

    try:
        encrypted_bytes = b64decode(value)
    except binascii.Error as error:
        raise EncryptionError(str(error))

    try:
        decrypted_bytes = box.decrypt(encrypted_bytes)
    except CryptoError as error:
        raise EncryptionError(str(error))

    return decrypted_bytes.decode(MESSAGE_ENCODING)


def rekey(encrypted, old_key=None, new_key=None):
    """Re-encrypted an encrypted message using a new key.

    Args:
        encrypted (str): An encrypted message to re-encrypt

    Keyword Args:
        old_key (bytes): The key used to encrypt the message
        new_key (bytes): The new key used to encrypt the message

    Raises:
        chiton.core.encryption.EncryptionError: If the re-encryption fails
    """
    decrypted_string = decrypt(encrypted, key=old_key or settings.CHITON_PREVIOUS_ENCRYPTION_KEY)
    return encrypt(decrypted_string, key=new_key or settings.CHITON_ENCRYPTION_KEY)


def _create_secret_box(key=None):
    """Create a secret box with a given key.

    Args:
        key [bytes]: A secret key

    Returns:
        nacl.secret.SecretBox: A secret box using the given key
    """
    try:
        return SecretBox(key or settings.CHITON_ENCRYPTION_KEY)
    except (TypeError, ValueError) as error:
        raise EncryptionError(str(error))
