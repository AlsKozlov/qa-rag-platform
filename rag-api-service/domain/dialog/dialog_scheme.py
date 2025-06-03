from database.database import BaseDB
from datetime import datetime
from sqlalchemy import Integer, DateTime, Text
from sqlalchemy.orm import mapped_column, Mapped


class Dialog(BaseDB):
    __tablename__ = "dialog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date_time_answer: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    dialog_history: Mapped[str] = mapped_column(Text, nullable=False)