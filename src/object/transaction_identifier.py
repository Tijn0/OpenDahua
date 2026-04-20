import random


class TransactionIdentifier:
    # Length constants.
    LENGTH_TRANSACTION_IDENTIFIER = 12
    
    def __init__(self, transaction_identifier_bytes: bytes):
        self._transaction_identifier_bytes: bytes = transaction_identifier_bytes
    
    @staticmethod
    def create_random() -> TransactionIdentifier:
        return TransactionIdentifier(
            random.randbytes(TransactionIdentifier.LENGTH_TRANSACTION_IDENTIFIER)
        )
    
    def get_transaction_identifier_bytes(self) -> bytes:
        return self._transaction_identifier_bytes
