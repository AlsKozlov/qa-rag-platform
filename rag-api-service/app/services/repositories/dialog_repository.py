from domain.dialog.dialog_scheme import Dialog
from database.database import session_maker
from sqlalchemy import insert, select, update, delete
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError


class DialogRepository():
    
    model = Dialog


    @classmethod
    async def find_one_or_none_by_conversation_id(cls, 
                                                  conversation_id: int,
                                                  session) -> Dialog:
        try:
            query = select(Dialog).where(
                Dialog.conversation_id == conversation_id
            )
            dialog = await session.execute(query)
            return dialog.scalar_one_or_none()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot find dialog " + str(e)
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot find dialog " + str(e) #TODO logger
            return None


    @classmethod
    async def add(cls, 
                  conversation_id: int,
                  date_time_answer: datetime,
                  dialog_history: str,
                  session):
        try:
            query = (
                insert(Dialog)
                .values(
                    conversation_id = conversation_id,
                    date_time_answer = date_time_answer,
                    dialog_history = dialog_history
                )
            )
            await session.execute(query)
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                print("Database Exc: Cannot add dialog " + str(e))
            elif isinstance(e, Exception):
                print("Unknown Exc: Cannot add dialog " + str(e)) #TODO logger


    @classmethod
    async def update_by_conversation_id(cls,
                                        conversation_id: int,
                                        date_time_answer: datetime,
                                        history: str,
                                        session):
        try:
            query = (
                update(Dialog)
                .where(
                    Dialog.conversation_id == conversation_id
                )
                .values(
                    dialog_history = history,
                    date_time_answer = date_time_answer
                )
            )
            await session.execute(query)
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot update dialog " + str(e)
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot update dialog " + str(e) #TODO logger


    @classmethod
    async def delete_by_conversation_id(cls,
                                        conversation_id: int,
                                        session):
        try:
            query = (
                delete(Dialog)
                .where(
                    Dialog.conversation_id == conversation_id
                )
            )
            await session.execute(query)
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot delete dialog " + str(e)
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot delete dialog " + str(e) #TODO logger