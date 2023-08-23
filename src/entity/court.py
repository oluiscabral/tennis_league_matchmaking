"""
author: oluiscabral
date: 8/23/23
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Court:
    name: str
