from time import time

from utility.printable import Printable

class Block(Printable):
    """Один блок нашего блокчейна.
    
    Attributes:
        :index: Индекс этого блока.
        :previous_hash: Хэш предыдущего блока в блокчейне.
        :timestamp: Отметка времени блока (автоматически генерируется по умолчанию).
        :transactions: Список транзакций, которые включены в блок.
        :proof: The proof of work который дал этот блок.
    """
    def __init__(self, index, previous_hash, transactions, proof, time=time()):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time
        self.transactions = transactions
        self.proof = proof


