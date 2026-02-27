-- PostgreSQL bootstrap script (credentials loaded from environment)
-- Usage:
--   set -a && source .env && set +a
--   sudo -E -u postgres psql -f scripts/postgres_setup.sql

\getenv app_db_user APP_DB_USER
\getenv app_db_password APP_DB_PASSWORD
\getenv app_db_name APP_DB_NAME

\if :{?app_db_user}
\else
\echo 'ERROR: missing APP_DB_USER in environment (.env)'
\quit 1
\endif

\if :{?app_db_password}
\else
\echo 'ERROR: missing APP_DB_PASSWORD in environment (.env)'
\quit 1
\endif

\if :{?app_db_name}
\else
\echo 'ERROR: missing APP_DB_NAME in environment (.env)'
\quit 1
\endif

SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'app_db_user', :'app_db_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'app_db_user')
\gexec

SELECT format('CREATE DATABASE %I OWNER %I', :'app_db_name', :'app_db_user')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'app_db_name')
\gexec

SELECT format('GRANT ALL PRIVILEGES ON DATABASE %I TO %I', :'app_db_name', :'app_db_user')
\gexec