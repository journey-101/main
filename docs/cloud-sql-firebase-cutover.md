# Cloud SQL and Firebase Auth cutover

## Scope and configuration

Application data remains in PostgreSQL/PostGIS. Firestore and Data Connect are not
used. The backend has one database contract, `DATABASE_URL`, plus pool controls:
`DATABASE_POOL_SIZE`, `DATABASE_MAX_OVERFLOW`, and `DATABASE_POOL_TIMEOUT`.

Firebase Admin uses Application Default Credentials and `GOOGLE_CLOUD_PROJECT` in
cloud environments. Local development additionally sets
`FIREBASE_AUTH_EMULATOR_HOST`. Never commit a service-account JSON file.
Cloud SQL supports the PostGIS extension used by these migrations; see the
[Cloud SQL extension list](https://docs.cloud.google.com/sql/docs/postgres/extensions).

## Local verification

```sh
docker compose up --build
docker compose --profile seed run --rm seed
```

The database is PostgreSQL 16 with PostGIS 3.5. The `migrate` service applies all
Alembic revisions before the backend starts. Seed data is a separate, idempotent
command and is never part of a production migration.

Create an emulator user and obtain an ID token through the Auth Emulator REST API,
then call protected routes as follows:

```sh
curl -H "Authorization: Bearer $FIREBASE_ID_TOKEN" \
  http://localhost:8000/api/v1/auth/me
```

## Existing database preparation

1. Verify that the database matches the legacy tables, then record the baseline:

   ```sh
   cd backend
   uv run alembic stamp 20260810_01
   ```

2. Export the finalized Firebase mapping with the exact header below. Every legacy
   user must appear exactly once and Firebase UIDs must be unique.

   ```csv
   legacy_user_uuid,firebase_uid
   00000000-0000-0000-0000-000000000000,actual-firebase-uid
   ```

3. Validate and stage it, then run the cutover revision:

   ```sh
   uv run python -m app.commands.map_legacy_users mapping.csv
   uv run alembic upgrade head
   ```

The mapping command validates everything before writing. The Alembic revision is
transactional and checks mapping coverage, orphan foreign keys, duplicate UIDs,
arrays, and place geometries before commit. The UID cutover is intentionally not
downgradable; rollback means restoring the backup.

Managed region boundaries are imported atomically from a GeoJSON FeatureCollection.
Each feature must have `properties.code`, `properties.name`, and a valid Polygon or
MultiPolygon geometry:

```sh
uv run python -m app.commands.import_regions regions.geojson
```

## Production runbook

Execute one controlled cutover:

1. Stop application writes.
2. Take and verify a restorable database backup.
3. Finalize Firebase users and the UUID-to-UID mapping.
4. Stamp the verified legacy baseline, stage the mapping, and apply Alembic.
5. Import authoritative region boundaries and any remaining managed data.
6. Run count, foreign-key, uniqueness, array, geometry, and API smoke checks.
7. Deploy the backend configured with Cloud SQL `DATABASE_URL`, ADC, and
   `GOOGLE_CLOUD_PROJECT`.
8. Keep the legacy database read-only until the rollback window closes.

Actual Cloud SQL creation, credential injection, Firebase client login UI, and
production traffic cutover are deliberately outside this repository change.
