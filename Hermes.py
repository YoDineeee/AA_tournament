import random
from collections import deque

#
PAYOFFS = {
    ('C', 'C'): (3, 3),  # Both cooperate
    ('C', 'D'): (0, 5),  # You cooperate, opponent defects
    ('D', 'C'): (5, 0),  # You defect, opponent cooperates
    ('D', 'D'): (1, 1),  # Both defect
}


class AdaptivePlayer:
   
    def __init__(
        self,
        total_rounds: int,
        window: int = 10,
        high_thresh: float = 0.7,
        low_thresh: float = 0.3,
        endgame_length: int = 5,
    ):
        self.total_rounds = total_rounds
        self.window = window
        self.high_thresh = high_thresh
        self.low_thresh = low_thresh
        self.endgame_length = endgame_length
        self.pattern_length = 3
        self.reset()

    def reset(self) -> None:
       
        self.my_history = []
        self.opp_history = []
        self.recent_moves = deque(maxlen=self.window)
        self.recent_coop_count = 0
        self.scores = {'me': 0, 'opponent': 0}
        self.aggressive_mode = False
        self.patterns = {}
        self.probing_rounds = 0
        
        
    def move(self, round_index: int) -> str:
      
        # Opening moves: establish trust
        if round_index < 2:
            return 'C'

        # Endgame strategy in final rounds
        if round_index >= self.total_rounds - self.endgame_length:
            return self._final_rounds(round_index)

        # Periodic probing to detect changes
        if round_index > 0 and round_index % 20 == 0:
            self.probing_rounds = 2
        if self.probing_rounds > 0:
            self.probing_rounds -= 1
            return random.choice(['C', 'D'])

        # Compute recent cooperation rate
        coop_rate = (
            self.recent_coop_count / len(self.recent_moves)
            if self.recent_moves
            else 0.5
        )

        # Pattern-based prediction
        if len(self.opp_history) >= self.pattern_length and self.probing_rounds == 0:
            pattern_move = self._predict_move()
            if pattern_move:
                return pattern_move

        # Score-based mode switch
        score_diff = self.scores['me'] - self.scores['opponent']
        if score_diff < -10:
            self.aggressive_mode = True
        elif score_diff > 5:
            self.aggressive_mode = False

        if self.aggressive_mode:
            return self._aggressive_play(coop_rate)

        # Strategy selection based on cooperation thresholds
        if coop_rate >= self.high_thresh:
            return self._mostly_cooperate()
        if coop_rate >= self.low_thresh:
            return self._forgive_defections(coop_rate)
        return self._mostly_defect()

    def record(self, my_move: str, opp_move: str) -> None:
       
        self.my_history.append(my_move)
        self.opp_history.append(opp_move)

        # Recent moves tracking and coop count
        if len(self.recent_moves) == self.window:
            if self.recent_moves[0] == 'C':
                self.recent_coop_count -= 1
        self.recent_moves.append(opp_move)
        if opp_move == 'C':
            self.recent_coop_count += 1

        # Score update
        me_score, opp_score = PAYOFFS[(my_move, opp_move)]
        self.scores['me'] += me_score
        self.scores['opponent'] += opp_score

        # Update pattern counts
        if len(self.opp_history) > self.pattern_length:
            self._update_patterns()

    def _update_patterns(self) -> None:
       
        i = len(self.opp_history) - self.pattern_length - 1
        pattern = ''.join(self.opp_history[i : i + self.pattern_length])
        next_move = self.opp_history[i + self.pattern_length]
        
        if pattern not in self.patterns:
            self.patterns[pattern] = {'C': 0, 'D': 0}
        self.patterns[pattern][next_move] += 1

    def _predict_move(self) -> str | None:
      
        recent_pattern = ''.join(self.opp_history[-self.pattern_length :])
        if recent_pattern not in self.patterns:
            return None
            
        counts = self.patterns[recent_pattern]
        if counts['C'] > 2 * counts['D']:
            return 'D'  # Opponent likely to cooperate, so defect
        if counts['D'] > 2 * counts['C']:
            return 'C'  # Opponent likely to defect, so cooperate
        return None

    def _mostly_cooperate(self) -> str:
     
        if random.random() < 0.95:
            return self.opp_history[-1]
        return 'D'

    def _forgive_defections(self, coop_rate: float) -> str:
      
        if self.opp_history[-1] == 'C':
            return 'C'
        forgiveness = 0.3 + (coop_rate * 0.5)
        return 'C' if random.random() < forgiveness else 'D'

    def _mostly_defect(self) -> str:
        
        if self.opp_history[-2:] == ['D', 'D'] and random.random() < 0.1:
            return 'C'
        return 'D'

    def _aggressive_play(self, coop_rate: float) -> str:
      
        last_two = self.opp_history[-2:]
        if coop_rate > 0.5 or last_two == ['C', 'C']:
            return 'D'
        if last_two == ['D', 'D']:
            return 'D'
        return self.opp_history[-1]

    def _final_rounds(self, round_index: int) -> str:
       
        rounds_left = self.total_rounds - round_index
        if self.recent_coop_count / len(self.recent_moves) > 0.8:
            return 'D'  # Defect against highly cooperative opponents
        if rounds_left <= 2 or self.opp_history[-1] == 'D':
            return 'D'  # Defect in last 2 rounds or if opponent just defected
        return self.opp_history[-1]  # Otherwise match opponent's last move

