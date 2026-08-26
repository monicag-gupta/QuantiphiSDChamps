# Cloud Run deployment notes
1. Build the container and push it to Artifact Registry.
2. Configure `DATABASE_URL` as a secret/environment variable; do not bake credentials into the image.
3. Connect Cloud Run to Cloud SQL using the supported Cloud SQL integration/private connectivity pattern.
4. Run Alembic migrations as a controlled deployment step before sending production traffic to the new revision.
5. Use a production process model, connection-pool limits appropriate for Cloud Run concurrency, structured logs and monitoring.
6. Replace the exercise `X-User-Id` header with real identity and authorization before production exposure.
