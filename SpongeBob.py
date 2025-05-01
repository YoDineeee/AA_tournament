def strategy(my_history: list[int], opponent_history: list[int], rounds: int | None) -> int:
    if not opponent_history:
        return 1

    total_rounds = len(opponent_history)

    if rounds is not None and total_rounds == rounds - 1:
        return 0

    window_size = min(5, total_rounds)
    recent_opponent_history = opponent_history[-window_size:]
    recent_opponent_defects = recent_opponent_history.count(0)

    opponent_defects = opponent_history.count(0)
    my_defects = my_history.count(0)

    if total_rounds >= 4:
        if all(opponent_history[-i] == opponent_history[-i-2] for i in range(1, 3)):
            expected_move = opponent_history[-2]
            return 1 - expected_move

    if total_rounds >= 2 and opponent_history[-1] == 0 and opponent_history[-2] == 0:
        return 0

    if opponent_defects / total_rounds > 0.5:
        if recent_opponent_defects / window_size < 0.4:
            return 1
        return 0

    if 1 <= total_rounds < 5:
        if opponent_history[-1] == 0:
            return 0

    if my_defects >= 10 and my_history[-2:].count(0) < 2:
        return 1

    return opponent_history[-1]
