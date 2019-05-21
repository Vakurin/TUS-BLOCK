class Printable:
    """Базовый класс, который реализует функции печати."""
    def __repr__(self):
        return str(self.__dict__)
