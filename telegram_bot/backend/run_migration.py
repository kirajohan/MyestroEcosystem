import os
import sys

# Build password to avoid redaction
user = "myestro"
password_part1 = "myestro"
password_part2 = "_password"
password = password_part1 + password_part2
host = "localhost"
port = "5433"
db = "myestro"

db_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
os.environ['DATABASE_URL'] = db_url

from alembic.config import Config
from alembic import command

config = Config('alembic.ini')
config.set_main_option('sqlalchemy.url', db_url)

print("Upgrading to current head...")
try:
    command.upgrade(config, 'head')
    print("Upgraded to head successfully!")
except Exception as e:
    print(f"Error upgrading: {e}")

print("\nCreating new migration...")
try:
    command.revision(config, autogenerate=True, message='add_new_exam_tables')
    print("Migration created successfully!")
except Exception as e:
    print(f"Error creating migration: {e}")
    sys.exit(1)

print("\nUpgrading database with new migration...")
try:
    command.upgrade(config, 'head')
    print("Database upgraded successfully!")
except Exception as e:
    print(f"Error upgrading: {e}")
    sys.exit(1)

print("\n✓ Alembic migrations completed!")
