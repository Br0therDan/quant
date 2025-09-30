from beanie import Document


class BaseDocument(Document):
    """Base document with common fields"""

    user_id: str | None = None

    class Settings:
        abstract = True
