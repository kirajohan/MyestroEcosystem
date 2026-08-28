$env:DATABASE_URL="postgresql://myestro:myestro_password@localhost:5433/myestro"
Set-Location "C:\Projects\MyestroEco\MyestroEco\telegram_bot\backend"
alembic revision --autogenerate -m "add_new_exam_tables"
alembic upgrade head
