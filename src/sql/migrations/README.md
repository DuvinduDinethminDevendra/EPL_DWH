Migration folder

- `000_create_schema.sql` - baseline canonical schema (placeholder)
- `001_hardening.sql` - small production hardening migration (audit columns, FK policies, indexes)

How to apply:
- Run the SQL files against your MySQL database in order. For local Docker container:

```powershell
# from repo root
docker exec -i epl_mysql mysql -uroot -p1234 epl_dw < src/sql/migrations/000_create_schema.sql
docker exec -i epl_mysql mysql -uroot -p1234 epl_dw < src/sql/migrations/001_hardening.sql
```

Recommendation: use a migration tool (Alembic, Flyway, Liquibase) to record applied migrations and run them idempotently.
