#!/usr/bin/env python3.11
"""Day 14: Parabolic Reflector Dish"""
import argparse
import sys


def calc_load(north_row: int, count: int, num_rows: int) -> int:
    """Given the row that the pile starts on from north, and the counts of rocks,
    calculate the total loads of the rocks in column."""
    return (num_rows - north_row + num_rows - north_row - count + 1) * count // 2


class Ground:
    """The ground class, to simulate the ground."""

    char_to_int_mapping = {
        ".": 0,
        "O": 1,
        "#": 2,
    }
    int_to_char_mapping = {v: k for k, v in char_to_int_mapping.items()}

    def __init__(self, input_ground: list[str]):
        self.ground: list[list[int]] = [
            list(map(lambda x: self.char_to_int_mapping[x], line))
            for line in input_ground
        ]
        # Copy the input ground
        self.num_rows = len(input_ground)
        self.num_cols = len(input_ground[0])

    def rotate_clock_wise(self) -> None:
        """Rotate the ground clock wise."""
        new_ground: list[list[int]] = [[] for _ in range(self.num_cols)]
        for row in range(self.num_rows - 1, -1, -1):
            for col, v in enumerate(self.ground[row]):
                new_ground[col].append(v)
        self.ground = new_ground
        self.num_rows, self.num_cols = self.num_cols, self.num_rows

    def slow_rotate_counter_clock_wise(self) -> None:
        """Rotate the ground counter clock wise.
        Not used in this problem too much, use a slower method."""
        for _ in range(3):
            self.rotate_clock_wise()

    def slide_left(self) -> None:
        """Slide all round rock left to the left most cubic rock or edge."""
        for row in range(self.num_rows):
            tail_col = 0
            line = self.ground[row]
            for col in range(self.num_cols):
                if line[col] == 2:
                    tail_col = col + 1
                elif line[col] == 1:
                    line[tail_col], line[col] = line[col], line[tail_col]
                    tail_col += 1

    def get_printable_ground(self) -> list[str]:
        """Get the printable ground."""
        return [
            "".join(
                map(
                    lambda x: self.int_to_char_mapping[x],
                    line,
                )
            )
            for line in self.ground
        ]

    def get_total_load_from_left(self) -> int:
        """Get the total load, counting from left as north."""
        total_loads = 0
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.ground[row][col] == 1:
                    total_loads += self.num_cols - col
        return total_loads


def solve_part_1(input_ground: list[str]) -> int:
    """To solve the part 1 of the problem."""
    # Calc the total loads of the rocks
    num_rows = len(input_ground)
    num_cols = len(input_ground[0])
    total_loads = 0
    for col in range(num_cols):
        north_row = 0
        count = 0
        for row in range(num_rows):
            if input_ground[row][col] == "#":
                total_loads += calc_load(north_row, count, num_rows)
                north_row = row + 1
                count = 0
            elif input_ground[row][col] == "O":
                count += 1
        total_loads += calc_load(north_row, count, num_rows)
    return total_loads


def solve_part_2(
    input_ground: list[str],
    num_cycles: int,
) -> int:
    """To solve the part 2 of the problem."""
    ground = Ground(input_ground=input_ground)
    # counter_clock_wise_rotate
    ground.slow_rotate_counter_clock_wise()
    # the ground must repeat itself, so we can use a dict to store the ground
    revisit_dict: dict[str, int] = {}

    # start the simulation
    i_cycle = 0
    found_cycle = 0  # the found repeat cycle, 0 for not found
    while i_cycle < num_cycles:
        # roll the rocks in 4 direction
        for _ in range(4):
            ground.slide_left()
            ground.rotate_clock_wise()
        if found_cycle == 0:
            ground_str = "".join(ground.get_printable_ground())
            if ground_str in revisit_dict:  # we found a loop!
                found_cycle = i_cycle - revisit_dict[ground_str]
                print(
                    f"Result of cycle {i_cycle} is the same as cycle {revisit_dict[ground_str]}. "
                    f"Found cycle = {found_cycle}",
                    file=sys.stderr,
                )
                i_cycle += (num_cycles - i_cycle) // found_cycle * found_cycle
            else:
                revisit_dict[ground_str] = i_cycle
        i_cycle += 1
    return ground.get_total_load_from_left()


def main():
    """Entrance of solution."""
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help="Input file")
    args = parser.parse_args()

    with open(args.input_file, "r", encoding="utf-8") as f:
        input_ground = [line.strip() for line in f.readlines()]

    print(
        solve_part_1(input_ground),
        solve_part_2(input_ground, 1000000000),
    )


if __name__ == "__main__":
    main()
