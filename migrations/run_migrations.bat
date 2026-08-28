@echo off
REM Migration Runner Script for Windows
REM Executes all SQL migrations in order from migrations/versions/

setlocal enabledelayedexpansion

REM Configuration
set MIGRATIONS_DIR=%cd%\migrations\versions
set MIGRATION_TRACKING_TABLE=migration_history

REM Database configuration from environment or defaults
if not defined DB_HOST set DB_HOST=localhost
if not defined DB_PORT set DB_PORT=5432
if not defined DB_USER set DB_USER=myestro
if not defined DB_NAME set DB_NAME=myestro
if not defined DB_PASSWORD (
    echo ERROR: DB_PASSWORD not set
    exit /b 1
)

echo.
echo 4 Starting Database Migrations
echo Host: %DB_HOST%:%DB_PORT% ^| Database: %DB_NAME% ^| User: %DB_USER%
echo.

REM Create migration tracking table
psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -c "CREATE TABLE IF NOT EXISTS %MIGRATION_TRACKING_TABLE% (id SERIAL PRIMARY KEY, version VARCHAR(50) NOT NULL UNIQUE, description TEXT, executed_at TIMESTAMPTZ DEFAULT NOW() NOT NULL, execution_time_ms INTEGER);" 2>nul

echo [OK] Migration tracking table ready
echo.

REM Count and execute migrations
setlocal enabledelayedexpansion
set EXECUTED_COUNT=0
set SKIPPED_COUNT=0

for /f "delims=" %%F in ('dir /b /on "%MIGRATIONS_DIR%\*.sql" 2^>nul') do (
    set MIGRATION_FILE=%%F
    set VERSION_NUM=!MIGRATION_FILE:_*=!
    set VERSION_NUM=!VERSION_NUM:~0,3!
    
    for /f %%X in ('psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -t -c "SELECT EXISTS(SELECT 1 FROM %MIGRATION_TRACKING_TABLE% WHERE version = '!VERSION_NUM!');" 2^>nul') do (
        if "%%X"=="t" (
            echo [SKIP] !MIGRATION_FILE! (already executed)
            set /a SKIPPED_COUNT+=1
        ) else (
            echo [RUN] !MIGRATION_FILE!...
            
            psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -f "%MIGRATIONS_DIR%\!MIGRATION_FILE!" >nul 2>&1
            
            if !errorlevel! equ 0 (
                psql -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -d %DB_NAME% -c "INSERT INTO %MIGRATION_TRACKING_TABLE% (version, description) VALUES ('!VERSION_NUM!', '!MIGRATION_FILE!') ON CONFLICT (version) DO NOTHING;" 2>nul
                echo [OK] !MIGRATION_FILE! completed
                set /a EXECUTED_COUNT+=1
            ) else (
                echo [ERROR] !MIGRATION_FILE! failed
            )
        )
    )
)

echo.
echo Migration Complete!
echo Executed: %EXECUTED_COUNT% ^| Skipped: %SKIPPED_COUNT%
echo.
