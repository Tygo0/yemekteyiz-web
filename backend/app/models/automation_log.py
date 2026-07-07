import enum
from datetime import datetime, timezone
from app.extensions import db


class AutomationImportStatus(enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class AutomationImportLog(db.Model):
    __tablename__ = "automation_import_logs"

    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(AutomationImportStatus), nullable=False)
    contestant_count = db.Column(db.Integer, nullable=False, default=0)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AutomationImportLog {self.id} week={self.week_id} {self.status.value}>"
