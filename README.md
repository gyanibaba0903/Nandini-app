# Nandini D1 V1

This is the first clean Nandini Worker using Cloudflare Python Workers + D1.

## Important
The D1 binding is intentionally added in the Cloudflare dashboard, so no database ID needs to be edited into this package.

1. Cloudflare -> Workers & Pages -> nandini-app -> Bindings.
2. Add binding -> D1 database.
3. Variable name: DB
4. Select: nandini-db
5. Save.

Then create the tables from `schema.sql` using the D1 dashboard SQL console.

After that, let the GitHub-connected deployment run.

The `/api/health` endpoint verifies that the Worker can actually talk to D1.
