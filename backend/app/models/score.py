from app.extensions import db


class Score(db.Model):
    __tablename__ = "scores"

    id = db.Column(db.Integer, primary_key=True)
    episode_id = db.Column(db.Integer, db.ForeignKey("episodes.id"), nullable=False)
    contestant_id = db.Column(db.Integer, db.ForeignKey("contestants.id"), nullable=False)

    # Who gave the score, e.g. "Zuhal" or another contestant's name.
    # Kept as a free-text field rather than a FK to a "Judge" table because
    # judges in this show are just the other contestants + Zuhal — modeling
    # a separate Judge entity would duplicate the Contestant table for no
    # benefit at this stage.
    judge_name = db.Column(db.String(150), nullable=False)
    value = db.Column(db.Integer, nullable=False)

    episode = db.relationship("Episode", back_populates="scores")
    contestant = db.relationship("Contestant", back_populates="scores_received")

    __table_args__ = (
        db.CheckConstraint("value >= 1 AND value <= 10", name="ck_score_value_range"),
    )

    def __repr__(self):
        return f"<Score {self.id} {self.judge_name}->{self.contestant_id}: {self.value}>"
