# Database migrations

## Argilla server database migrations

Since Argilla 1.6.0, the information about users and workspaces, and the data of the `Dataset`s is stored in an SQL database (SQLite or PostgreSQL). That being said,
every release of Argilla may require a database migration to update the database schema to the new version. This section explains how to perform the database migrations.

To apply the migrations, a connection to the database needs to be established. In the case that SQLite is used, then the only way to apply the migrations is by
executing the migration command from the same machine where the Argilla server is running. In the case that PostgreSQL is used, then the migration command can be executed
from any machine that has access to the PostgreSQL database setting the `ARGILLA_DATABASE_URL` environment variable to the URL of the database.

### Listing the available database revisions/migrations

To list the available database revisions/migrations, the `argilla server database revisions` command can be used. This command will list the different revisions to which
the database can be migrated. As several revisions could be generated for a single release, the command will also show the latest revision that was generated for each release.

```bash
argilla server database revisions
```

```bash
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.

Tagged revisions
-----------------
• 1.7 (revision: '1769ee58fbb4')
• 1.8 (revision: 'ae5522b4c674')
• 1.11 (revision: '3ff6484f8b37')
• 1.13 (revision: '1e629a913727')

Alembic revisions
-----------------
3fc3c0839959 -> 1e629a913727 (head), fix suggestions type enum values
8c574ada5e5f -> 3fc3c0839959, create suggestions table
3ff6484f8b37 -> 8c574ada5e5f, update_enum_columns
ae5522b4c674 -> 3ff6484f8b37, add record metadata column
e402e9d9245e -> ae5522b4c674, create fields table
8be56284dac0 -> e402e9d9245e, create responses table
3a8e2f9b5dea -> 8be56284dac0, create records table
b9099dc08489 -> 3a8e2f9b5dea, create questions table
1769ee58fbb4 -> b9099dc08489, create datasets table
82a5a88a3fa5 -> 1769ee58fbb4, create workspaces_users table
74694870197c -> 82a5a88a3fa5, create workspaces table
<base> -> 74694870197c, create users table

Current revision
----------------
Current revision(s) for sqlite:////Users/gabrielmbmb/.argilla/argilla.db?check_same_thread=False:
Rev: 1e629a913727 (head)
Parent: 3fc3c0839959
Path: /Users/gabrielmbmb/Source/Argilla/argilla/src/argilla/server/alembic/versions/1e629a913727_fix_suggestions_type_enum_values.py

    fix suggestions type enum values

    Revision ID: 1e629a913727
    Revises: 3fc3c0839959
    Create Date: 2023-07-24 12:47:11.715011
```

### Apply the latest migration

If the `migrate` command is called without any argument, then the latest migration will be applied.

```bash
argilla server database migrate
```

### Apply a specific migration

The `migrate` command can also be used to apply a specific migration. To do so, the `--revision` option needs to be provided with the name of the revision or the Argilla
version to which the database will be migrated.

```bash
argilla server database migrate migrate --revision 1.7
```

!!! warning
    Applying a revision that is older than the current revision of the database will revert the database to the state of that revision, which means that the data could be lost.
