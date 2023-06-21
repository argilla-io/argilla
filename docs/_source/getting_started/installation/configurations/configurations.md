(configurations)=
# ⚙️ Configuration

````{grid}  1 1 3 3
:class-container: tuto-section-2
```{grid-item-card} ElasticSearch
:link: elasticsearch.md

Tweak your elastic configs:
- Configure roles and users
- Change index analyzers
- Reindex data
- Backups using snapshots
```
```{grid-item-card} Server Configuration
:link: server_configuration.md

Finetune your FastAPI deployment:
- Launching FastAPI
- Environment variables
- REST API docs
```
```{grid-item-card} User Management
:link: user_management.md

Manage your Argilla users:
- User model
- Prepare the DB
- Get default user
- Create a new user
- Assign a user to a workspace
- List all the existing users
- Delete a user
- Migrate users from `users.yaml`
- Migration users with Docker Compose
```
```{grid-item-card} Workspace Management
:link: workspace_management.md

Manage your Argilla workspaces:
- Workspace model
- Create a new workspace
- List all the existing workspaces
- Get a workspace by name
- Get a workspace by id
- Add, list, or delete users from a workspace
```

```{grid-item-card} Database Migrations
:link: database_migrations.md

Dealing with database migrations:
- Migrating from old schema
- Reindex a dataset
```

```{grid-item-card} Image Support
:link: image_support.md

Multimodality at your fingertips:
- `_image_url` as special `metadata`-field
- An applied tutorial by Ben Burtenshaw
```
````

```{toctree}
:hidden:

elasticsearch.md
server_configuration.md
user_management.md
workspace_management.md
database_migrations.md
image_support.md
```