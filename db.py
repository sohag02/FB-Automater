from sqlalchemy import create_engine, Column, String, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

# supress logs
# Suppress SQLAlchemy engine logs
logger = logging.getLogger(__name__)


# logging = logging.getlogging(__name__)
# logging.propagate = False
# Define the database URL
DATABASE_URL = "sqlite:///./data.db"

# Create an engine that stores data in the local directory's data.db file
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

# Create a base class
Base = declarative_base()

# Define the model
class UserProfile(Base):
    __tablename__ = 'user_profiles'
    
    session = Column(String, primary_key=True)
    last_post_date = Column(Date, nullable=False)
    profile_setup = Column(Boolean, nullable=False)

# Create the table in the database
Base.metadata.create_all(engine)

# Create a new session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def insert_user_profile(email, last_post_date_str, profile_setup):
    session = SessionLocal()
    try:
        # last_post_date = datetime.strptime(last_post_date_str, '%d-%m-%Y').date()
        user_profile = UserProfile(
            session=email,
            last_post_date=last_post_date_str,
            profile_setup=profile_setup
        )
        session.add(user_profile)
        session.commit()
        logging.info(f"Added profile: {email}")
    except Exception as e:
        logging.error(f"Error in process: {e}")
        session.rollback()
    finally:
        session.close()

def get_user_profile(email):
    session = SessionLocal()
    try:
        user_profile = session.query(UserProfile).filter_by(session=email).first()
        if user_profile:
            return user_profile
        else:
            return None
    except Exception as e:
        logging.error(f"Error in process: {e}")
        session.rollback()
    finally:
        session.close()

def update_user_profile(email, last_post_date=None, profile_setup=None):
    session = SessionLocal()
    try:
        user_profile = session.query(UserProfile).filter_by(session=email).first()
        if user_profile:
            if last_post_date:
                user_profile.last_post_date = last_post_date
            if profile_setup:
                user_profile.profile_setup = profile_setup
            session.commit()
            logging.info(f"Updated profile: {email}")
        else:
            logging.error(f"Profile not found: {email}")
    except Exception as e:
        logging.error(f"Error in process: {e}")
        session.rollback()
    finally:
        session.close()

def delete_user_profile(email):
    try:
        session = SessionLocal()
        user_profile = session.query(UserProfile).filter_by(session=email).first()
        if user_profile:
            session.delete(user_profile)
            session.commit()
            logging.info(f"Deleted profile: {email}")
        else:
            logging.error(f"Profile not found: {email}")
    except Exception as e:
        logging.error(f"Error in process: {e}")
        session.rollback()
    finally:
        session.close()

def get_all_user_profiles():
    session = SessionLocal()
    try:
        user_profiles = session.query(UserProfile).all()
        return user_profiles
    except Exception as e:
        logging.error(f"Error in process: {e}")
        session.rollback()
    finally:
        session.close()