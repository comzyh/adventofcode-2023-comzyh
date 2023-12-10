import argparse
from collections import Counter
from functools import cache

_card_values = list(reversed("A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2".split(", ")))


@cache
def hand_order_key(hand: str) -> tuple[int, int]:
    """Return a tuple of the hand order key"""
    value = 0
    for card in hand:
        value *= len(_card_values)
        value += _card_values.index(card)

    counter = Counter(hand)
    counts = sorted(list(counter.items()), key=lambda x: x[1], reverse=True)
    if counts[0][1] == 5:  # Five of a kind
        return (6, value)
    elif counts[0][1] == 4:  # Four of a kind
        return (5, value)
    elif counts[0][1] == 3:
        if counts[1][1] == 2:  # Full house
            return (4, value)
        else:  # Three of a kind
            return (3, value)
    elif counts[0][1] == 2:
        if counts[1][1] == 2:  # Two pair
            return (2, value)
        else:  # One pair
            return (1, value)
    else:  # High card
        return (0, value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help="Input file")
    args = parser.parse_args()

    with open(args.input_file) as f:
        hands_bid = [line.strip().split() for line in f.readlines()]

    sorted_hands = sorted(hands_bid, key=lambda x: hand_order_key(x[0]))
    answer = 0

    for index, bid in enumerate(sorted_hands):
        answer += (index + 1) * int(bid[1])
    print(answer)


if __name__ == "__main__":
    main()
