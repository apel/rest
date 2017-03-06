# Schema Naming Conventions
The schema files here are pre-fixed with a numeral to insure their alphanumeric order is the same order that the schema files should be applied to a fresh MySQL installation / container. 

This is due to the way the APEL database is deployed as a docker container.

Schema files are mounted into the directory `/docker-entrypoint-initdb.d` within the standard [MySQL Docker Image](https://hub.docker.com/r/library/mysql/) and are automatically executed in alphanumeric order when the container starts for the first time to create the database.

`20-cloud-extra.sql` assumes the presence of tables created in `10-cloud.sql`.

Without these numeral prefixes, `cloud-extra.sql` would be executed first, resulting in a failure to create the database as it would refer to tables that had not yet been created.

Future schema files **must** continue this naming convention when they depend on other schema files present in this directory. Schema files without such dependencies should continue this convention, but can be executed in any order.
