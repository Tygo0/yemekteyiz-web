from datetime import datetime, timezone
from app.extensions import db


class Week(db.Model):
    __tablename__ = "weeks"

    id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey("seasons.id"), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    air_date = db.Column(db.Date, nullable=True)
    youtube_url = db.Column(db.String(500), nullable=True)

    # Nullable + set after the week's episodes have all been scored.
    # Uses use_alter/post_update to break the circular FK dependency with
    # Contestant.week_id (a week has many contestants, but also points back
    # to exactly one of them as the winner).
    winner_id = db.Column(
        db.Integer,
        db.ForeignKey("contestants.id", use_alter=True, name="fk_week_winner"),
        nullable=True,
    )
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    season = db.relationship("Season", back_populates="weeks")
    contestants = db.relationship(
        "Contestant",
        back_populates="week",
        cascade="all, delete-orphan",
        foreign_keys="Contestant.week_id",
    )
    winner = db.relationship("Contestant", foreign_keys=[winner_id], post_update=True)

    __table_args__ = (
        db.UniqueConstraint("season_id", "week_number", name="uq_season_week_number"),
    )

    def __repr__(self):
        return f"<Week {self.id} season={self.season_id} #{self.week_number}>"
