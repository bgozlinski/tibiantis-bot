import logging
from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any

T = TypeVar('T')

logger = logging.getLogger(__name__)


class BaseRepository(Generic[T]):
    """
    Base repository class providing common database operations.
    
    This class serves as a foundation for specific repository implementations,
    providing common CRUD operations and transaction management.
    
    Attributes:
        db (Session): SQLAlchemy database session
        model_class (Type[T]): The SQLAlchemy model class this repository manages
    """
    
    def __init__(self, db: Session, model_class: Type[T]):
        """
        Initialize repository with database session and model class.
        
        Parameters:
            db (Session): SQLAlchemy database session
            model_class (Type[T]): The SQLAlchemy model class this repository manages
        """
        self.db = db
        self.model_class = model_class
    
    def get_all(self) -> List[T]:
        """
        Retrieve all entities of the managed model from the database.
        
        Returns:
            List[T]: List of all entities
        """
        return self.db.query(self.model_class).all()
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Retrieve an entity by its ID.
        
        Parameters:
            entity_id (int): The ID of the entity to retrieve
            
        Returns:
            Optional[T]: Found entity or None if not found
        """
        return self.db.query(self.model_class).filter(self.model_class.id == entity_id).first()
    
    def create(self, entity: T) -> T:
        """
        Add a new entity to the database.
        
        Parameters:
            entity (T): The entity to add
            
        Returns:
            T: The added entity with its ID populated
            
        Raises:
            Exception: If there's an error in adding the entity to the database
        """
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            logger.info(f"Successfully added {self.model_class.__name__} to database (ID: {entity.id})")
            return entity
        except Exception as e:
            logger.error(f"Error adding {self.model_class.__name__} to database: {e}", exc_info=True)
            self.db.rollback()
            raise
    
    def update(self, entity_id: int, update_data: Dict[str, Any]) -> Optional[T]:
        """
        Update an entity by ID with the provided data.
        
        Parameters:
            entity_id (int): The ID of the entity to update
            update_data (Dict[str, Any]): Dictionary containing the fields to update
            
        Returns:
            Optional[T]: Updated entity or None if not found
            
        Raises:
            Exception: If there's an error in updating the entity in the database
        """
        entity = self.get_by_id(entity_id)
        
        if not entity:
            return None
        
        logger.info(f"Updating {self.model_class.__name__} (ID: {entity_id})")
        
        for key, value in update_data.items():
            if hasattr(entity, key) and value is not None:
                setattr(entity, key, value)
        
        try:
            self.db.commit()
            self.db.refresh(entity)
            logger.info(f"Successfully updated {self.model_class.__name__} (ID: {entity_id})")
            return entity
        except Exception as e:
            logger.error(f"Error updating {self.model_class.__name__} in database: {e}", exc_info=True)
            self.db.rollback()
            raise
    
    def delete(self, entity_id: int) -> bool:
        """
        Delete an entity by ID.
        
        Parameters:
            entity_id (int): The ID of the entity to delete
            
        Returns:
            bool: True if the entity was deleted, False if it wasn't found
            
        Raises:
            Exception: If there's an error in deleting the entity from the database
        """
        entity = self.get_by_id(entity_id)
        
        if not entity:
            return False
        
        logger.info(f"Deleting {self.model_class.__name__} (ID: {entity_id})")
        
        try:
            self.db.delete(entity)
            self.db.commit()
            logger.info(f"Successfully deleted {self.model_class.__name__} (ID: {entity_id})")
            return True
        except Exception as e:
            logger.error(f"Error deleting {self.model_class.__name__} from database: {e}", exc_info=True)
            self.db.rollback()
            raise