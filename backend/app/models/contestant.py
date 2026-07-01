from datetime import datetime, timezone
from app.extensions import db


class Contestant(db.Model):
    __tablename__ = "contestants"

    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey("weeks.id"), nullable=False)

    name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    profession = db.Column(db.String(150), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    biography = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    week = db.relationship(
        "Week", back_populates="contestants", foreign_keys=[week_id]
    )
    episodes = db.relationship(
        "Episode", back_populates="contestant", cascade="all, delete-orphan"
    )
    scores_received = db.relationship(
        "Score", back_populates="contestant", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Contestant {self.id} {self.name}>"
