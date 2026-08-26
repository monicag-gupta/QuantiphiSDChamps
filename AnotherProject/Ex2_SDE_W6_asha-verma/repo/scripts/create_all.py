from src.db.base import Base
from src.db.session import engine
import src.models.orm  # noqa: F401


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("ProjectFlow tables created successfully.")
