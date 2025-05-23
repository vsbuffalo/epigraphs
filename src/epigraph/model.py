from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class Node:
    id: str
    label: Optional[str] = None
    style: Dict[str, str] = field(default_factory=dict)


@dataclass
class Edge:
    source: str
    target: str
    label: Optional[str] = None
    style: Dict[str, str] = field(default_factory=dict)
