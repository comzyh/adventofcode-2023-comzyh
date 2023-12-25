#!/usr/bin/env python3.11
"""Day 20: Pulse Propagation"""
import argparse
from collections import defaultdict, Counter, deque
from enum import Enum
import sys


class ModuleType(Enum):
    """Module type."""

    FLIP_FLOP = 1
    CONJUNCTION = 2
    BROADCAST = 3


class Machines:
    """Machines that contains modules."""

    def __init__(
        self,
        modules: list[tuple[ModuleType, list[int]]],
        module_name_to_index: dict[str, int],
    ):
        """Initialize."""
        self.modules = modules
        self.module_name = {v: k for k, v in module_name_to_index.items()}
        # internal state
        self.state: list[int] = []
        """The internal states of 0 or 1.
        For Flip-flop, 1 for on and 0 for off
        For Conjunction, remember all the inputs, 1 for high and 0 for low
        """
        self._module_to_state: dict[int, list[int]] = defaultdict(list)
        """ given a module index, return the state index"""
        self._output_states: list[list[tuple[int, int]]] = []
        """The module index and state index that all output controls"""
        self._conjunction_sum: defaultdict[int, int] = defaultdict(int)
        """Remember the sum of all inputs for conjunctions"""
        self.broadcast = -1
        """The index of broad case module"""

        # Init the broadcast module, have the fake state index = 0
        self.state.append(0)
        # First pass, init all Flip-flop and self.broadcast
        for module_index, (module_type, _) in enumerate(modules):
            if module_type == ModuleType.FLIP_FLOP:
                self.state.append(0)
                self._module_to_state[module_index].append(len(self.state) - 1)
            elif module_type == ModuleType.BROADCAST:
                self.broadcast = module_index
                self._module_to_state[module_index].append(0)
        # Second pass, init all outputs to Conjunction
        for module_index, (module_type, outputs) in enumerate(modules):
            output_state_index: list[tuple[int, int]] = []
            for output in outputs:
                if output >= len(self.modules):
                    # controls nothing but still a pulse
                    output_state_index.append((output, -1))
                    continue
                if self.modules[output][0] == ModuleType.CONJUNCTION:
                    self.state.append(0)  # Conjunction remember all input to be low
                    self._module_to_state[output].append(len(self.state) - 1)
                    output_state_index.append((output, len(self.state) - 1))
                else:
                    output_state_index.append(
                        (output, self._module_to_state[output][0])
                    )
            self._output_states.append(output_state_index)

    def debug_pulse(self, source_index: int, target_index: int, level: int) -> None:
        """Output the debug info"""
        source = self.module_name[source_index]
        target = self.module_name[target_index]
        level_name = "high" if level == 1 else "low"
        print(f"{source} -{level_name}-> {target}", file=sys.stderr)

    def run(self, debug=False) -> tuple[int, int]:
        """Run the machines."""
        Pulse = tuple[int, int, int]  # module_index, state_index, level
        q: deque[Pulse] = deque()
        counter: Counter[int] = Counter()
        q.append(
            (self.broadcast, 0, 0)
        )  # Start from the pulse to broadcast module with low level
        while q:
            module_index, state_index, level = q.popleft()
            counter[level] += 1  # count the pulse
            if state_index < 0:  # skip the fake state that won't propagate
                continue
            module_type, _ = self.modules[module_index]
            outputs = self._output_states[module_index]
            output_level = -1  # do not propagate
            if module_type == ModuleType.FLIP_FLOP:
                if level == 1:
                    continue  # Flip-flop will do nothing if the level is high
                self.state[state_index] = 1 - self.state[state_index]
                output_level = self.state[state_index]
            elif module_type == ModuleType.CONJUNCTION:
                self._conjunction_sum[module_index] += level - self.state[state_index]
                self.state[state_index] = level
                if self._conjunction_sum[module_index] == len(
                    self._module_to_state[module_index]
                ):
                    # if it remembers high pulses for all inputs, it sends a low pulse
                    output_level = 0
                else:
                    # otherwise, it sends a high pulse.
                    output_level = 1
            elif module_type == ModuleType.BROADCAST:
                output_level = level

            if output_level == -1:  # No output
                continue
            for output_index, output_state_index in outputs:
                if debug:
                    self.debug_pulse(module_index, output_index, output_level)
                q.append((output_index, output_state_index, output_level))

        return counter[1], counter[0]


def parse_modules(
    input_lines: list[str],
) -> tuple[list[tuple[ModuleType, list[int]]], dict[str, int]]:
    """Parse modules from input lines."""
    module_index: dict[str, int] = {}
    module_type: list[ModuleType] = []

    # First pass, get name -> index mapping
    for line_no, line in enumerate(input_lines):
        module_str, _ = line.split(" -> ")
        if module_str.startswith("%"):  # Flip-flop
            module_name = module_str[1:]
            module_type.append(ModuleType.FLIP_FLOP)
        elif module_str.startswith("&"):  # Conjunction
            module_name = module_str[1:]
            module_type.append(ModuleType.CONJUNCTION)
        else:
            module_name = module_str
            module_type.append(ModuleType.BROADCAST)
        module_index[module_name] = line_no

    # Second pass, parse all modules
    modules: list[tuple[ModuleType, list[int]]] = []
    for line_no, line in enumerate(input_lines):
        # Parse output ports
        _, output_ports_str = line.split(" -> ")
        output_ports = output_ports_str.split(", ")
        outputs = []
        for output_port in output_ports:
            if output_port not in module_index:
                module_index[output_port] = len(module_index)
            output_port_index = module_index[output_port]
            outputs.append(output_port_index)
        modules.append((module_type[line_no], outputs))

    return modules, module_index


def main():
    """Entrance of solution."""
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help="Input file")
    args = parser.parse_args()

    with open(args.input_file, "r", encoding="utf-8") as f:
        input_lines = [line.strip() for line in f.readlines()]
    modules, module_name_to_index = parse_modules(input_lines=input_lines)
    machine = Machines(modules, module_name_to_index)

    # simulate
    total_high_pulse, total_low_pulse = 0, 0
    for _ in range(1000):
        high_pulse, low_pulse = machine.run(debug=True)
        total_high_pulse += high_pulse
        total_low_pulse += low_pulse

    print(total_high_pulse, total_low_pulse, file=sys.stderr)
    print(total_high_pulse * total_low_pulse)


if __name__ == "__main__":
    main()
