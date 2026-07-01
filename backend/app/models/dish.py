import enum
from app.extensions import db


class DishCategory(enum.Enum):
    SOUP = "soup"
    APPETIZER = "appetizer"
    MAIN_COURSE = "main_course"
    DESSERT = "dessert"
    BEVERAGE = "beverage"


class Dish(db.Model):
    __tablename__ = "dishes"

    id = db.Column(db.Integer, primary_key=True)
    episode_id = db.Column(db.Integer, db.ForeignKey("episodes.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.Enum(DishCategory), nullable=False)

    episode = db.relationship("Episode", back_populates="dishes")

    def __repr__(self):
        return f"<Dish {self.id} {self.name} ({self.category.value})>"
