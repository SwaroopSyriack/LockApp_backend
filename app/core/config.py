from dotenv import load_dotenv
load_dotenv()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY : str
    DB_URL : str


    class Config:
        env_file = ".env"





settings = Settings()
