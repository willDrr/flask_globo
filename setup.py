from app import create_app, db, celery
from app.models import User
from flask_migrate import Migrate
from app.seed import seed_db

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, seed_db=seed_db)
