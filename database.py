
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl": {
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
        "ssl_ca": "C:\\Users\\Midhun\\Documents\\certs\\isrgrootx1.pem"
    }
    }
)

SessionLocal = sessionmaker(bind = engine)
Base = declarative_base()
