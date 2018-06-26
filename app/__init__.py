from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO, emit
from threading import Lock

async_mode = None

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app=app)
migrate = Migrate(app=app, db=db)
login = LoginManager(app=app)
bootstrap = Bootstrap(app=app)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


from app import routes, models

socketio.run(app)
#app.run()