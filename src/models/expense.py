"""
Expense Domain Model.
Represents a financial expense transaction.
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Expense:
    """Represents a single expense transaction."""
    date: str
    category: str
    amount: float
    payment_method: str
    description: str = ""
    is_synthetic: int = 0
    id: Optional[int] = None
    created_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert the dataclass instance to a dictionary."""
        return asdict(self)
