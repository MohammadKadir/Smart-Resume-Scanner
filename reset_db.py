from app.database import engine
from app.models import Base

print("Clearing database tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("Database reset cleanly!")
