@echo off
setlocal

set "CURR_DIR=%~dp0"
set "DB_NAME=%USERNAME%_eBay_DB"

call "%CURR_DIR%startPostgreSQL.bat"
call "%CURR_DIR%createPostgreDB.bat"

psql -p %PGPORT% -d %DB_NAME% -f "%CURR_DIR%create_tables.sql"
psql -p %PGPORT% -d %DB_NAME% -f "%CURR_DIR%initial_data.sql"
psql -p %PGPORT% -d %DB_NAME% -f "%CURR_DIR%indexes.sql"