in an iterative app we use nosql_yorm as our nosql ORM, we have a
we also use a testing cached mechanism found in nosql_yorm that allows us to use the normal ORM functions like get_by_id, get_page, merge, get_by_ids, get_all, and save

class IterativeModel(BaseModel, Generic[T]):
    """
    Base model for Firebase entities. 
    Includes basic fields and methods for interacting with Firestore.
    """
    id: Optional[str] = Field(default_factory=lambda: None)
    __collection_name__: str = ""
    created_at: Optional[datetime] = Field(default_factory=lambda: None)
    updated_at: Optional[datetime] = Field(default_factory=lambda: None)

    @classmethod
    def _get_collection_name(cls):
        """
        Get the collection name for the model. 
        Defaults to the pluralized class name if __collection_name__ is not set.
        """
        return cls.__collection_name__ or p.plural(cls.__name__)

    @classmethod
    def get_by_id(cls: Type[T], doc_id: str, namespace: str = "User",
                  read_write_to_cache: Optional[bool] = None) -> Optional[T]:
        """
        Retrieve a document by its ID.
        
        Args:
            cls: The class type to return.
            doc_id: The document ID to retrieve.
            namespace: The namespace (for caching).
            read_write_to_cache: Whether to read/write to the cache.

        Returns:
            An instance of the document if found, otherwise None.
        """
        # Method implementation...

    @classmethod
    def get_by_ids(cls: Type[T], doc_ids: List[str], namespace: str = "User",
                   read_write_to_cache: Optional[bool] = None) -> List[T]:
        """
        Retrieve multiple documents by their IDs.
        
        Args:
            cls: The class type to return.
            doc_ids: A list of document IDs to retrieve.
            namespace: The namespace (for caching).
            read_write_to_cache: Whether to read/write to the cache.

        Returns:
            A list of document instances.
        """
        # Method implementation...

    @classmethod
    def get_page(cls: Type[T], namespace: str = "User", page: int = 1,
                 page_size: int = 10, query_params: Optional[Dict[str, Any]] = None,
                 array_contains: Optional[Dict[str, Any]] = None,
                 read_write_to_cache: Optional[bool] = None) -> List[T]:
        """
        Retrieve a paginated list of documents.
        
        Args:
            cls: The class type to return.
            namespace: The namespace (for caching).
            page: The page number to retrieve.
            page_size: The number of documents per page.
            query_params: Parameters to filter the query.
            array_contains: Parameters for 'array_contains' queries.
            read_write_to_cache: Whether to read/write to the cache.

        Returns:
            A list of document instances for the specified page.
        """
        # Method implementation...

    @classmethod
    def get_all(cls: Type[T], read_write_to_cache: Optional[bool] = None,
                namespace: str = "Users") -> List[T]:
        """
        Retrieve all documents from the collection.

        Args:
            cls: The class type to return.
            read_write_to_cache: Whether to read/write to the cache.
            namespace: The namespace (for caching).

        Returns:
            A list of all document instances in the collection.
        """
        # Method implementation...

    def save(self, generate_new_id: bool = False, 
             read_write_to_cache: Optional[bool] = None, namespace: str = "User") -> None:
        """
        Save the current instance to Firestore.

        Args:
            generate_new_id: Whether to generate a new ID for the document.
            read_write_to_cache: Whether to read/write to the cache.
            namespace: The namespace (for caching).
        """
        # Method implementation...

    def delete(self, read_write_to_cache: Optional[bool] = None, namespace: str = "Users") -> None:
        """
        Delete the current document from Firestore.

        Args:
            read_write_to_cache: Whether to read/write to the cache.
            namespace: The namespace (for caching).
        """
        # Method implementation...

    def merge(self, update_data: Dict[str, Any], overwrite_id: bool = False,
              exclude_props: List[str] = [], read_write_to_cache: Optional[bool] = None,
              namespace: str = "Users") -> None:
        """
        Merge new data into the current document instance and update Firestore.

        Args:
            update_data: The data to merge into the current instance.
            overwrite_id: Whether to overwrite the document ID.
            exclude_props: Properties to exclude from the update.
            read_write_to_cache: Whether to read/write to the cache.
            namespace: The namespace (for caching).
        """
        # Method implementation...

    @staticmethod
    def generate_fake_firebase_id() -> str:
        """
        Generate a fake Firestore document ID

