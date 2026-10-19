"""
Budget Domain Model.
Represents a monthly or category-level budget allocation.
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Budget:
    """Represents a budget target for a month and category."""
    month: str  # Format: YYYY-MM
    category: str  # 'OVERALL' or specific category name
    allocated_amount: float
    id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert the dataclass instance to a dictionary."""
        return asdict(self)
