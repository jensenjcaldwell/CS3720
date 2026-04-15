from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class QueryLog(db.Model):
    """
    Stores a record of every analysis query submitted through the UI.

    Demonstrates Tier 3 (Data Layer): persists user interactions in SQLite
    via SQLAlchemy so the app can display a query history page.
    """

    __tablename__ = "query_log"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    analysis_type = db.Column(db.String(50), nullable=False)   # describe | missing | histogram | scatter | bar
    column_name = db.Column(db.String(100), nullable=False)
    second_column = db.Column(db.String(100), nullable=True)   # scatter plots only
    location_filter = db.Column(db.String(100), nullable=True) # None means all locations

    def __repr__(self):
        return (
            f"<QueryLog id={self.id} type={self.analysis_type} "
            f"col={self.column_name} @ {self.timestamp}>"
        )
