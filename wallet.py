import logging
import binascii
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

logger = logging.getLogger(__name__)


class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def create_keys(self):
        """
        Function to create private and public keys to validate transactions
        """
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def save_keys(self):
        """
        Function to save keys to the disk
        """
        if not (self.public_key is None and self.private_key is None):
            try:
                with open('wallet.txt', 'w') as f:
                    f.write(self.public_key)
                    f.write("\n")
                    f.write(self.private_key)
                return True
            except (IOError,
                    IndexError):  # IndexError - File exists but is empty
                logger.error('Saving wallet failed')
                print('Saving wallet failed')
                return False

    def load_keys(self):
        """
        Function to load keys from the disk
        """
        try:
            with open('wallet.txt', 'r') as f:
                keys = f.readlines()
                # All characters except the line break
                self.public_key = keys[0][:-1]
                self.private_key = keys[1]
            return True
        except (IOError, IndexError):
            logger.error('Loading wallet failed')
            print('Loading wallet failed')
            return False

    def generate_keys(self):
        """
        Function to generate private and public keys
        """
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        # Returning string representation of the key
        return (binascii.hexlify(
            private_key.exportKey(format='DER')).decode('ascii'),
                binascii.hexlify(
                    public_key.exportKey(format='DER')).decode('ascii'))

    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(
            RSA.importKey(binascii.unhexlify(self.private_key)))
        hhash = SHA256.new(
            (str(sender) + str(recipient) + str(amount)).encode('utf8'))

        signature = signer.sign(hhash)
        return binascii.hexlify(signature).decode('ascii')

    @staticmethod
    def verify_transaction_signature(transaction):
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        hhash = SHA256.new(
            (str(transaction.sender) + str(transaction.recipient) +
             str(transaction.amount)).encode('utf8'))

        return verifier.verify(hhash, binascii.unhexlify(
            transaction.signature))  # Returns Boolean value
