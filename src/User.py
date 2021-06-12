from src.cthulhu import Cthulhu


class User:
    def __init__(self, cthulhu: Cthulhu):
        self.balance = cthulhu.get_balance()
        self.open_orders = cthulhu.get_open_orders()
        self.closed_orders = cthulhu.get_closed_orders()


