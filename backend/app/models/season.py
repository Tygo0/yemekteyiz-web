from datetime import datetime, timezone
from app.extensions import db


class Season(db.Model):
    __tablename__ = "seasons"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    weeks = db.relationship(
        "Week", back_populates="season", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Season {self.id} {self.name} ({self.year})>"
