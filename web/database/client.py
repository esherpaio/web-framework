from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from web.config import config

engine = create_engine(config.DATABASE_URL, echo=False)
conn = sessionmaker(engine, autoflush=False, expire_on_commit=False)
