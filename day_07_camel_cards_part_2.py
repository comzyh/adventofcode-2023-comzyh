import argparse
from collections import Counter
from functools import cache

_card_values = list(reversed("A, K, Q, T, 9, 8, 7, 6, 5, 4, 3, 2, J".split(", ")))


@cache
def hand_order_key(hand: str) -> tuple[int, int]:
    """Return a tuple of the hand order key"""
    value = 0
    for card in hand:
        value *= len(_card_values)
        value += _card_values.index(card)

    counter = Counter(hand)
    j_count = counter["J"]
    if "J" in counter:
        counter.pop("J")
    counts = sorted(list(counter.values()), reverse=True) + [0] * (5 - len(counter))
    # Five of a kind
    if j_count == 5 or counts[0] + j_count == 5:
        return (6, value)
    # Four of a kind
    elif j_count == 4 or counts[0] + j_count == 4:
        return (5, value)
    # Full house
    elif j_count == 3 and counts[0] == 2:
        return (4, value)
    elif counts[0] + j_count == 3 and counts[1] == 2:
        return (4, value)
    elif counts[0] == 3 and (counts[1] + j_count == 2):
        return (4, value)
    # Three of a kind
    elif counts[0] + j_count == 3:
        return (3, value)
    # Two pair
    elif counts[0] == 2 and counts[1] + j_count == 2:
        return (2, value)
    # One pair
    elif counts[0] + j_count == 2:
        return (1, value)
    # High card
    else:
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
