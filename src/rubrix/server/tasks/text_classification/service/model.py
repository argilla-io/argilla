from dataclasses import dataclass, field
from typing import Optional, Set, Union


@dataclass
class Dataset:
    """Text classification dataset structure"""

    name: str

    labels: Optional[Union[Set[str], Set[int]]] = field(default_factory=set)
    multi_label: bool = False
