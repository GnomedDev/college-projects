from typing import Optional

def linear_search(array: list[int], item: int) -> Optional[int]:
    return next((i for i, v in enumerate(array) if v == item), None)

__all__ = ("linear_search",)
