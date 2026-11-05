from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# For SQLite database, use the following URL format:
# SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"

# For PostgreSQL database, use the following URL format:
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres.jvlxledtccuznmoivrlh:787AdminNazrul@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"

#For PostgreSQL database, use the following URL format:
# SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:password@localhost/TodosApplicationDatabase"
#For SQLite database, use connect_args={"check_same_thread": False} to avoid threading issues. For PostgreSQL, this argument is not needed.
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# For MySQL database, use the following URL format:
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/TodosApplicationDatabase"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# check

# postgresql://postgres.jvlxledtccuznmoivrlh:[YOUR-PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres