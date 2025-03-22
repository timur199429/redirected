import os
from sqlmodel import SQLModel, create_engine, Session


# Create the database engine
URL_DATABASE = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(URL_DATABASE)

def db_init():
    # Create all tables in the database
    SQLModel.metadata.create_all(engine)


# Dependency: Get the session
def get_session():
    with Session(engine) as session:
        yield session