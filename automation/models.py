"""
Shared data structures passed between pipeline stages. Kept independent of any
one stage's implementation (mock or real) so downloader/extractor/ocr/vision/
speech implementations can be swapped without touching parser/validator/api_client.
"""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class DishData:
    name: str
    category: str  # soup | appetizer | main_course | dessert | beverage


@dataclass
class ScoreData:
    judge_name: str
    value: int


@dataclass
class ContestantData:
    name: str
    age: Optional[int] = None
    profession: Optional[str] = None
    city: Optional[str] = None
    biography: Optional[str] = None
    photo_url: Optional[str] = None
    broadcast_date: Optional[date] = None
    video_url: Optional[str] = None
    dishes: list[DishData] = field(default_factory=list)
    scores: list[ScoreData] = field(default_factory=list)


@dataclass
class WeekImportPayload:
    week_id: int
    contestants: list[ContestantData] = field(default_factory=list)

    def to_api_dict(self) -> dict:
        return {
            "week_id": self.week_id,
            "contestants": [
                {
                    "name": c.name,
                    "age": c.age,
                    "profession": c.profession,
                    "city": c.city,
                    "biography": c.biography,
                    "photo_url": c.photo_url,
                    "broadcast_date": c.broadcast_date.isoformat() if c.broadcast_date else None,
                    "video_url": c.video_url,
                    "dishes": [{"name": d.name, "category": d.category} for d in c.dishes],
                    "scores": [{"judge_name": s.judge_name, "value": s.value} for s in c.scores],
                }
                for c in self.contestants
            ],
        }
