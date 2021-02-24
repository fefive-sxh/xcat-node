from app.xcat_api import app
from base.database import create_tables

if __name__ == '__main__':
    create_tables()
    app.run()
