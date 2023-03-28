# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `ARGILLA_HOME_PATH` new environment variable ([#2564]).
- `ARGILLA_DATABASE_URL` new environment variable ([#2564]).
- Basic support for user roles with `admin` and `annotator` ([#2564]).
- `id`, `first_name`, `last_name`, `role`, `inserted_at` and `updated_at` new user fields ([#2564]).
- `/api/users` new endpoint to list and create users ([#2564]).
- `/api/users/{user_id}` new endpoint to delete users ([#2564]).
- `/api/workspaces` new endpoint to list and create workspaces ([#2564]).
- `/api/workspaces/{workspace_id}/users` new endpoint to list workspace users ([#2564]).
- `/api/workspaces/{workspace_id}/users/{user_id}` new endpoint to create and delete workspace users ([#2564]).
- `argilla.tasks.users.migrate` new task to migrate users from old YAML file to database ([#2564]).
- `argilla.tasks.users.create` new task to create a user ([#2564]).
- `argilla.tasks.users.create_default` new task to create a user with default credentials ([#2564]).
- `argilla.tasks.database.migrate` new task to execute database migrations ([#2564]).
- `release.Dockerfile` and `quickstart.Dockerfile` now creates a default `argilladata` volume to persist data ([#2564]).

### Changed

- `ARGILLA_USERS_DB_FILE` environment variable now it's only used to migrate users from YAML file to database ([#2564]).
- `full_name` user field is now deprecated and `first_name` and `last_name` should be used instead ([#2564]).
- `password` user field now requires a minimum of `8` and a maximum of `100` characters in size ([#2564]).
- `quickstart.Dockerfile` image default users from `team` and `argilla` to `admin` and `annotator` including new passwords and API keys ([#2564]).
- Datasets to be managed only by users with `admin` role ([#2564]).

### Fixes

- Copying datasets between workspaces with proper owner/workspace info. Closes [#2562](https://github.com/argilla-io/argilla/issues/2562)
- Using elasticsearch config to request backend version. Closes [#2311](https://github.com/argilla-io/argilla/issues/2311)


### Removed

- `email` user field ([#2564]).
- `disabled` user field ([#2564]).
- Support for private workspaces ([#2564]).
- `ARGILLA_LOCAL_AUTH_DEFAULT_APIKEY` and `ARGILLA_LOCAL_AUTH_DEFAULT_PASSWORD` environment variables. Use `python -m argilla.tasks.users.create_default` instead ([#2564]).

[#2564]: https://github.com/argilla-io/argilla/issues/2564


## [1.5.0](https://github.com/recognai/rubrix/compare/v1.4.0...v1.5.0) - 2023-03-21

### Added

- Add the fields to retrieve when loading the data from argilla. `rg.load` takes too long because of the vector field, even when users don't need it. Closes [#2398](https://github.com/argilla-io/argilla/issues/2398)
- Add new page and components for dataset settings. Closes [#2442](https://github.com/argilla-io/argilla/issues/2003)
- Add ability to show image in records (for TokenClassification and TextClassification) if an URL is passed in metadata with the key \_image_url
- Non-searchable fields support in metadata. [#2570](https://github.com/argilla-io/argilla/pull/2570)
- add user settings page [#2496](https://github.com/argilla-io/argilla/issues/2496)
- Add record ID references to the prepare for training methods. Closes [#2483](https://github.com/argilla-io/argilla/issues/2483)
- Add tutorial on Image Classification. [#2420](https://github.com/argilla-io/argilla/pull/2420)

### Changed

- Labels are now centralized in a specific vuex ORM called GlobalLabel Model, see https://github.com/argilla-io/argilla/issues/2210. This model is the same for TokenClassification and TextClassification (so both task have labels with color_id and shortcuts parameters in the vuex ORM)
- The shortcuts improvement for labels [#2339](https://github.com/argilla-io/argilla/pull/2339) have been moved to the vuex ORM in dataset settings feature [#2444](https://github.com/argilla-io/argilla/commit/eb37c3bcff3ad253481d6a10f8abb093384f2dcb)
- Update "Define a labeling schema" section in docs.
- The record inputs are sorted alphabetically in UI by default. [#2581](https://github.com/argilla-io/argilla/pull/2581)
- The record inputs are fully visible when pagination size is one and the height of collapsed area size is bigger for laptop screen. [#2587](https://github.com/argilla-io/argilla/pull/2587/files)

### Fixes

- Allow URL to be clickable in Jupyter notebook again. Closes [#2527](https://github.com/argilla-io/argilla/issues/2527)

### Removed

- Removing some data scan deprecated endpoints used by old clients. This change will break compatibility with client `<v1.3.0`
- Stop using old scan deprecated endpoints in python client. This logic will break client compatibility with server version `<1.3.0`
- Remove the previous way to add labels through the dataset page. Now labels can be added only through dataset settings page.
