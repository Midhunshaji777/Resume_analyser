
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if os.name == 'nt' :
    ssl_ca_path = "C:\\Users\\Midhun\\Documents\\certs\\isrgrootx1.pem"
else:
    ssl_ca_path = "/etc/ssl/certs/ca-certificates.crt"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "ssl": {
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
        "ssl_ca": ssl_ca_path
    }
    }
)

SessionLocal = sessionmaker(bind = engine)
Base = declarative_base()
