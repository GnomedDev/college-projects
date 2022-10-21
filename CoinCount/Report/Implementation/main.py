from __future__ import annotations

import contextlib
import dataclasses
import json
import math
from enum import Enum
from typing import Callable, Optional, TypedDict

import tabulate


def clear_screen():
    print("\33[H\33[2J\33[3J", end="")

def increment_total(volunteer: Volunteer) -> Volunteer:
    volunteer["total_bags"] += 1

    return volunteer

def increment_correct(volunteer: Volunteer) -> Volunteer:
    volunteer["correct_bags"] += 1

    return increment_total(volunteer)

def with_data(volunteer: str, callback: Callable[[Volunteer], Optional[Volunteer]]):
    with open("CoinCount.txt") as file:
        data: dict[str, Volunteer] = json.load(file)

    new_volunteer = callback(data.get(volunteer, {"correct_bags": 0, "total_bags": 0}))

    if new_volunteer is None:
        return

    data[volunteer] = new_volunteer
    with open("CoinCount.txt", "w") as file:
        json.dump(data, file)


class CoinType(Enum):
    POUND_2 = 200
    POUND_1 = 100
    P_50 = 50
    P_20 = 20
    P_10 = 10
    P_5 = 5
    P_2 = 2
    P_1 = 1

    def __str__(self) -> str:  # sourcery skip: assign-if-exp
        if "POUND" in self.name:
            return f"£{self.value / 100:.2f}"
        else:
            return f"{self.value}p"

    @classmethod
    def from_human(cls, repr: str) -> Optional[CoinType]:
        if repr.startswith("£"):
            repr_cleaned = repr[1::]
            template_str = "POUND_{}"
        elif repr.endswith("p"):
            repr_cleaned = repr[:-1:]
            template_str = "P_{}"
        else:
            return None

        try:
            repr_i = int(float(repr_cleaned))
        except ValueError:
            return None

        return getattr(cls, template_str.format(str(repr_i)), None)

class Volunteer(TypedDict):
    total_bags: int
    correct_bags: int

@dataclasses.dataclass
class BagInfo:
    coin_weight: float
    expected_value: float

bag_lookup: dict[CoinType, BagInfo] = {
    CoinType.POUND_2: BagInfo(12.00, 20),
    CoinType.POUND_1: BagInfo(8.75, 20),
    CoinType.P_50:    BagInfo(8.00, 10),
    CoinType.P_20:    BagInfo(5.00, 10),
    CoinType.P_10:    BagInfo(6.50, 5),
    CoinType.P_5:     BagInfo(2.35, 5),
    CoinType.P_2:     BagInfo(7.12, 1),
    CoinType.P_1:     BagInfo(3.56, 1),
}


class MenuOption:
    def __init__(self, name: str, callback: Callable[[], None]) -> None:
        self.name = name
        self.callback = callback


class Menu:
    options: list[MenuOption]
    def __init__(self, options: list[MenuOption]) -> None:
        self.options = options

    def __str__(self) -> str:
        return "\n".join(
            f"{index + 1}: {option.name}"
            for index, option in enumerate(self.options)
        )

    def run(self):
        while True:
            clear_screen()
            print(self)

            try:
                option_idx_str = input("Enter an option: ")
            except KeyboardInterrupt:
                break

            try:
                option_idx = int(option_idx_str) - 1
            except ValueError:
                continue

            self.options[option_idx].callback()

def input_coin_type() -> CoinType:
    while True:
        clear_screen()

        print("Acceptable Coins:")
        print("\n".join(map(str, CoinType)))

        coin_type_str = input("Enter coin type: ").lower()
        coin_type = CoinType.from_human(coin_type_str)

        if coin_type is not None:
            return coin_type

def input_weight() -> float:
    weight = float("NAN")
    while not math.isfinite(weight):
        clear_screen()
        weight = float(input("Enter weight: "))

    return weight


def start_validate():
    while True:
        clear_screen()

        name = input("Enter volunteer name: ")
        coin_type = input_coin_type()
        bag_weight = input_weight()

        bag_info = bag_lookup[coin_type]
        coin_value: int = coin_type.value

        bag_coin_num = (bag_info.expected_value * 100) / coin_value
        expected_bag_weight = bag_coin_num * bag_info.coin_weight

        offset = expected_bag_weight - bag_weight

        if offset == 0:
            with_data(name, increment_correct)
        else:
            if offset > 0:
                action = "add"
                from_or_to = "to"
            else:
                action = "remove"
                from_or_to = "from"
                offset = offset * -1

            coin_offset = offset // bag_info.coin_weight
            input(f"Please {action} {coin_offset} coins {from_or_to} the bag in order to correct the weight.\n")

            with_data(name, increment_total)

def view_data():
    clear_screen()
    with open("CoinCount.txt") as file:
        data: dict[str, Volunteer] = json.load(file)

    if data:
        names = list(data.keys())
        tabular_data: list[tuple[str, int, int, str]] = []
        for idx, volunteer in enumerate(data.values()):
            correct = volunteer["correct_bags"]
            total = volunteer["total_bags"]

            tabular_data.append((names[idx], correct, total, f"{(correct / total) * 100:.2f}%"))

        tabular_data.sort(key=lambda v: v[3], reverse=True)

        print(tabulate.tabulate(tabular_data, headers=["Name", "Correct", "Total", "Accuracy"]))
    else:
        print("No volunteer data entered!")

    input()
    clear_screen()

with contextlib.suppress(KeyboardInterrupt):
    Menu([
        MenuOption(name="Validate coin bag", callback=start_validate),
        MenuOption(name="View saved data", callback=view_data),
    ]).run()
