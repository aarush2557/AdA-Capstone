"""
models.py
=========
Defines the basic data structure used by the whole project: the Parcel.

A parcel has FIVE attributes (this is the "data design" asked for in Phase 1):

    parcel_id       -> unique number of the parcel (1, 2, 3, ...)
    destination     -> node number of the delivery point in the road graph
    weight          -> weight in whole kilograms (integer, needed by the knapsack DP)
    deadline_hours  -> hours from "now" within which the parcel must be delivered
    priority        -> 1 (low) ... 5 (very high), e.g. 5 = medical / express parcel

From these we derive ONE more number, the parcel's "value" (importance score),
which is what the knapsack algorithm tries to maximise.
"""

from dataclasses import dataclass, asdict


@dataclass
class Parcel:
    """One parcel that the courier has to deliver."""

    parcel_id: int
    destination: int
    weight: int
    deadline_hours: int
    priority: int

    @property
    def value(self) -> int:
        """
        Importance score of the parcel (used as the 'profit' in the knapsack).

        value = priority * 10  +  urgency_bonus

        * priority * 10 : a priority-5 parcel is worth 50 points, priority-1 is 10.
        * urgency_bonus : parcels with a short deadline get extra points.
                          bonus = (48 - deadline_hours) // 6, never below 0.
                          So a parcel due in 2 hours gets +7, one due in 48 hours +0.

        The value is an INTEGER on purpose - integer values keep the DP table
        simple and exact (no floating point rounding problems).
        """
        urgency_bonus = max(0, 48 - self.deadline_hours) // 6
        return self.priority * 10 + urgency_bonus

    # ---- helper methods used when saving / loading datasets as JSON ----
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Parcel":
        return cls(**data)
