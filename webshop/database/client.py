from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from webshop import config

Engine = create_engine(config.DATABASE_URL, echo=False)
Conn = sessionmaker(Engine, autoflush=False, expire_on_commit=False)
