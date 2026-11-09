# Alembic

Database migration configuration is intentionally left minimal in the MVP.
Once PostgreSQL persistence is wired into AnalysisService, initialize Alembic
and generate the first migration from the SQLAlchemy models.
