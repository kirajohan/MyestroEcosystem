#!/usr/bin/env python3
import os
import sys
os.chdir(r'C:\Projects\MyestroEco\MyestroEco\telegram_bot\backend')
sys.path.insert(0, r'C:\Projects\MyestroEco\MyestroEco\telegram_bot\backend')

# Set the database URL with actual password
os.environ['DATABASE_URL'] = 'postgresql://myestro:[REDACTED]@localhost:5433/myestro'

from alembic.config import Config
from alembic import command

# Load alembic config
config = Config('alembic.ini')
config.set_main_option('sqlalchemy.url', os.environ['DATABASE_URL'])

# Run revision
print("Creating migration...")
command.revision(config, autogenerate=True, message='add_new_exam_tables')

# Run upgrade
print("Upgrading database...")
command.upgrade(config, 'head')

print("Done!")
