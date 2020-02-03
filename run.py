from app import app
from db import db
import os

db.init_app(app)

@app.before_first_request
def create_tables():
    try:
      db.create_all()
    except:
      print(os.environ.get("DATABASE_URL"))
