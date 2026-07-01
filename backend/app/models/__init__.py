"""
Import every model here so that:
1. `from app.models import Season, Week, ...` works from anywhere.
2. Flask-Migrate's autogenerate can discover all tables via db.metadata
   (models that are never imported are invisible to Alembic).
"""
from app.models.season import Season
from app.models.week import Week
from app.models.contestant import Contestant
from app.models.episode import Episode
from app.models.dish import Dish, DishCategory
from app.models.score import Score
from app.models.admin import Admin

__all__ = [
    "Season",
    "Week",
    "Contestant",
    "Episode",
    "Dish",
    "DishCategory",
    "Score",
    "Admin",
]
