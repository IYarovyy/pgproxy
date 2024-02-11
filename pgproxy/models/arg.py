from dataclasses import dataclass


@dataclass
class Arg:
    name: str
    type: str
    mode: str
