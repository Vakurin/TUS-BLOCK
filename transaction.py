from collections import OrderedDict

from utility.printable import Printable

class Transaction(Printable):
    """Транзакция которая добавляет блок в блокчейн.

    Attributes:
        :sender: Имя отправителя.
        :recipient: Получатель имя.
        :signature: Подпись транзакции.
        :amount: Отправленная оценка.
    """
    def __init__(self, sender, recipient, signature, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_ordered_dict(self):
        """Конвертирует транзакцию в хэш Словаря (hashable) OrderedDict."""
        return OrderedDict([('sender', self.sender), ('recipient', self.recipient), ('amount', self.amount)])
