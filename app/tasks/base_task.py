import logging
from contextlib import contextmanager
from sqlalchemy.orm import Session
from app.db.dependecies import get_db

logger = logging.getLogger(__name__)


class BaseTask:
    """
    Base class for tasks providing common functionality.
    
    This class provides common functionality for tasks, such as database session management
    and error handling.
    """
    
    @contextmanager
    def get_db_session(self):
        """
        Context manager for database sessions.
        
        This method provides a database session and ensures it is properly closed
        after use, even if an exception occurs.
        
        Yields:
            Session: SQLAlchemy database session
            
        Example:
            task = SomeTask()
            with task.get_db_session() as db:
                # Use db session
                characters = db.query(Character).all()
        """
        db = next(get_db())
        try:
            yield db
        except Exception as e:
            logger.error(f"Error in task with database session: {e}", exc_info=True)
            db.rollback()
            raise
        finally:
            db.close()
    
    def execute_with_session(self, func, *args, **kwargs):
        """
        Execute a function with a database session.
        
        This method provides a database session to the function and ensures it is properly closed
        after use, even if an exception occurs.
        
        Parameters:
            func (callable): Function to execute with a database session
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Any: Result of the function
            
        Example:
            task = SomeTask()
            result = task.execute_with_session(lambda db: db.query(Character).all())
        """
        with self.get_db_session() as db:
            return func(db, *args, **kwargs)