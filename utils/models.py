from dataclasses import dataclass
from typing import Optional


@dataclass
class FunctionResult:
    """Estrutura tipada para armazenar resultado por função."""
    cdfg: Optional[str]
    infeasible_paths: Optional[str]
