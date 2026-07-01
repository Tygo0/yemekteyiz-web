from datetime import datetime, timezone
from app.extensions import db


class Episode(db.Model):
    __tablename__ = "episodes"

    id = db.Column(db.Integer, primary_key=True)
    contestant_id = db.Column(db.Integer, db.ForeignKey("contestants.id"), nullable=False)

    broadcast_date = db.Column(db.Date, nullable=True)
    video_url = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    contestant = db.relationship("Contestant", back_populates="episodes")
    dishes = db.relationship(
        "Dish", back_populates="episode", cascade="all, delete-orphan"
    )
    scores = db.relationship(
        "Score", back_populates="episode", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Episode {self.id} contestant={self.contestant_id}>"
