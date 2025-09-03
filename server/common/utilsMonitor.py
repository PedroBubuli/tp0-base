from . import utils
import threading

class UtilsMonitor:
    def __init__(self):
        self._lock = threading.Lock()

    def store_bet(self, bets: list[utils.Bet]) -> None:
        with self._lock:
            utils.store_bets(bets)

    def load_winners(self, agency_id: int) -> list[utils.Bet]:
        with self._lock:
            winners = []
            for bet in utils.load_bets():
                if utils.has_won(bet):
                    if bet.agency == agency_id:
                        winners.append(int(bet.document))
            return winners