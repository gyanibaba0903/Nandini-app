# Nandini Free AI V2

This version connects the live chat to Cloudflare Workers AI and D1.

Workers AI currently provides 10,000 free neurons per day on the Workers Free plan.
The selected model is `@cf/zai-org/glm-4.7-flash`, which is listed as available on
the Workers Free plan.

Required bindings:
- AI -> Workers AI
- DB -> nandini-db

The D1 tables are defined in schema.sql.
