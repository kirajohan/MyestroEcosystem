#!/usr/bin/env python
import sys
sys.path.insert(0, '/app')
import os
from alembic.config import Config
from alembic.command import upgrade

cfg = Config('/app/alembic.ini')
db_url = os.getenv('DATABASE_URL')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
cfg.set_main_option('sqlalchemy.url', db_url)
upgrade(cfg, 'head')
print('Migration completed successfully!')
