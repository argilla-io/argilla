# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semanti
c Versioning](https://semver.org/spec/v2.0.0.html).

<!--
These are the section headers that we use:
* "Added" for new features.
* "Changed" for changes in existing functionality.
* "Deprecated" for soon-to-be removed features.
* "Removed" for now removed features.
* "Fixed" for any bug fixes.
* "Security" in case of vulnerabilities.
-->

## [Unreleased]

### Added

- Added `RankingQuestionSettings` class allowing to create ranking questions in the API using `POST /api/v1/datasets/{dataset_id}/questions` endpoint ([#3232](https://github.com/argilla-io/argilla/pull/3232))

## [1.11.0](https://github.com/argilla-io/argilla/compare/v1.10.0...v1.11.0)

### Fixed

- Replaced `np.float` alias by `float` to avoid `AttributeError` when using `find_label_errors` function with `numpy>=1.24.0` ([#3214](https://github.com/argilla-io/argilla/pull/3214)).
- Fixed `format_as("datasets")` when no responses or optional respones in `FeedbackRecord`, to set their value to what 🤗 Datasets expects instead of just `None` ([#3224](https://github.com/argilla-io/argilla/pull/3224)).
- Fixed `push_to_huggingface()` when `generate_card=True` (default behaviour), as we were passing a sample record to the `ArgillaDatasetCard` class, and `UUID`s introduced in 1.10.0 ([#3192](https://github.com/argilla-io/argilla/pull/3192)), are not JSON-serializable ([#3231](https://github.com/argilla-io/argilla/pull/3231)).
- Fixed `from_argilla` and `push_to_argilla` to ensure consistency on both field and question re-construction, and to ensure `UUID`s are properly serialized as `str`, respectively ([#3234](https://github.com/argilla-io/argilla/pull/3234)).

#### Docs

- Fixed URLs in Weak Supervision with Sentence Tranformers tutorial [#3241](https://github.com/argilla-io/argilla/pull/3241).
- Fixed library buttons' formatting on Tutorials page [#2819](https://github.com/argilla-io/argilla/pull/2819).

### Added

- Added `metadata` attribute to the `Record` of the `FeedbackDataset` ([#3194](https://github.com/argilla-io/argilla/pull/3194))
- New `users update` command to update the role for an existing user ([#3188](https://github.com/argilla-io/argilla/pull/3188))
- New `Workspace` class to allow users manage their Argilla workspaces and the users assigned to those workspaces via the Python client ([#3180](https://github.com/argilla-io/argilla/pull/3180))
- Added `User` class to let users manage their Argilla users via the Python client ([#3169](https://github.com/argilla-io/argilla/pull/3169)).
- Added an option to display `tqdm` progress bar to `FeedbackDataset.push_to_argilla` when looping over the records to upload ([#3233](https://github.com/argilla-io/argilla/pull/3233)).

### Changed

- The role system now support three different roles `owner`, `admin` and `annotator` ([#3104](https://github.com/argilla-io/argilla/pull/3104))
- `admin` role is scoped to workspace-level operations ([#3115](https://github.com/argilla-io/argilla/pull/3115))
- The `owner` user is created among the default pool of users in the quickstart, and the default user in the server has now `owner` role ([#3248](https://github.com/argilla-io/argilla/pull/3248)), reverting ([#3188](https://github.com/argilla-io/argilla/pull/3188)).

### Deprecated

- As of Python 3.7 end-of-life (EOL) on 2023-06-27, Argilla will no longer support Python 3.7 ([#3188](https://github.com/argilla-io/argilla/pull/33188)). More information at https://peps.python.org/pep-0537/

## [1.10.0](https://github.com/argilla-io/argilla/compare/v1.9.0...v1.10.0)

### Added

- Added search component for feedback datasets ([#3138](https://github.com/argilla-io/argilla/pull/3138))
- Added markdown support for feedback dataset guidelines ([#3153](https://github.com/argilla-io/argilla/pull/3153))
- Added Train button for feedback datasets ([#3170](https://github.com/argilla-io/argilla/pull/3170))

### Changed

- Updated `SearchEngine` and `POST /api/v1/me/datasets/{dataset_id}/records/search` to return the `total` number of records matching the search query ([#3166](https://github.com/argilla-io/argilla/pull/3166))

### Fixed

- Replaced Enum for string value in URLs for client API calls (Closes [#3149](https://github.com/argilla-io/argilla/issues/3149))
- Resolve breaking issue with `ArgillaSpanMarkerTrainer` for Named Entity Recognition with `span_marker` v1.1.x onwards.
- Move `ArgillaDatasetCard` import under `@requires_version` decorator, so that the `ImportError` on `huggingface_hub` is handled properly ([#3174](https://github.com/argilla-io/argilla/pull/3174))
- Allow flow `FeedbackDataset.from_argilla` -> `FeedbackDataset.push_to_argilla` under different dataset names and/or workspaces ([#3192](https://github.com/argilla-io/argilla/issues/3192))

### Docs

- Resolved typos in the docs ([#3238](https://github.com/argilla-io/argilla/issues/3238))
- Fixed mention of master branch [#2324](https://github.com/argilla-io/argilla/pull/2324).


## [1.9.0](https://github.com/argilla-io/argilla/compare/v1.8.0...v1.9.0)

### Added

- Added boolean `use_markdown` property to `TextFieldSettings` model.
- Added boolean `use_markdown` property to `TextQuestionSettings` model.
- Added new status `draft` for the `Response` model.
- Added `LabelSelectionQuestionSettings` class allowing to create label selection (single-choice) questions in the API ([#3005](https://github.com/argilla-io/argilla/pull/3005))
- Added `MultiLabelSelectionQuestionSettings` class allowing to create multi-label selection (multi-choice) questions in the API ([#3010](https://github.com/argilla-io/argilla/pull/3010)).
- Added `POST /api/v1/me/datasets/{dataset_id}/records/search` endpoint ([#3068](https://github.com/argilla-io/argilla/pull/3068)).
- Added new components in feedback task Question form: MultiLabel ([#3064](https://github.com/argilla-io/argilla/pull/3064)) and SingleLabel ([#3016](https://github.com/argilla-io/argilla/pull/3016)).
- Added docstrings to the `pydantic.BaseModel`s defined at `argilla/client/feedback/schemas.py` ([#3137](https://github.com/argilla-io/argilla/pull/3137))

### Changed

- Updated `GET /api/v1/me/datasets/:dataset_id/metrics` output payload to include the count of responses with `draft` status.
- Added `LabelSelectionQuestionSettings` class allowing to create label selection (single-choice) questions in the API.
- Added `MultiLabelSelectionQuestionSettings` class allowing to create multi-label selection (multi-choice) questions in the API.
- Database setup for unit tests. Now the unit tests use a different database than the one used by the local Argilla server (Closes [#2987](https://github.com/argilla-io/argilla/issues/2987)).
- Updated `alembic` setup to be able to autogenerate revision/migration scripts using SQLAlchemy metadata from Argilla server models ([#3044](https://github.com/argilla-io/argilla/pull/3044))
- Improved `DatasetCard` generation on `FeedbackDataset.push_to_huggingface` when `generate_card=True`, following the official HuggingFace Hub template, but suited to `FeedbackDataset`s from Argilla ([#3110](https://github.com/argilla-io/argilla/pull/3100))

### Fixed

- Disallow `fields` and `questions` in `FeedbackDataset` with the same name ([#3126]).
- Fixed broken links in the documentation and updated the development branch name from `development` to `develop` ([#3145]).

[#3126]: https://github.com/argilla-io/argilla/pull/3126

## [1.8.0](https://github.com/argilla-io/argilla/compare/v1.7.0...v1.8.0)

### Added

- `/api/v1/datasets` new endpoint to list and create datasets ([#2615]).
- `/api/v1/datasets/{dataset_id}` new endpoint to get and delete datasets ([#2615]).
- `/api/v1/datasets/{dataset_id}/publish` new endpoint to publish a dataset ([#2615]).
- `/api/v1/datasets/{dataset_id}/questions` new endpoint to list and create dataset questions ([#2615])
- `/api/v1/datasets/{dataset_id}/fields` new endpoint to list and create dataset fields ([#2615])
- `/api/v1/datasets/{dataset_id}/questions/{question_id}` new endpoint to delete a dataset questions ([#2615])
- `/api/v1/datasets/{dataset_id}/fields/{field_id}` new endpoint to delete a dataset field ([#2615])
- `/api/v1/workspaces/{workspace_id}` new endpoint to get workspaces by id ([#2615])
- `/api/v1/responses/{response_id}` new endpoint to update and delete a response ([#2615])
- `/api/v1/datasets/{dataset_id}/records` new endpoint to create and list dataset records ([#2615])
- `/api/v1/me/datasets` new endpoint to list user visible datasets ([#2615])
- `/api/v1/me/dataset/{dataset_id}/records` new endpoint to list dataset records with user responses ([#2615])
- `/api/v1/me/datasets/{dataset_id}/metrics` new endpoint to get the dataset user metrics ([#2615])
- `/api/v1/me/records/{record_id}/responses` new endpoint to create record user responses ([#2615])
- showing new feedback task datasets in datasets list ([#2719])
- new page for feedback task ([#2680])
- show feedback task metrics ([#2822])
- user can delete dataset in dataset settings page ([#2792])
- Support for `FeedbackDataset` in Python client (parent PR [#2615], and nested PRs: [#2949], [#2827], [#2943], [#2945], [#2962], and [#3003])
- Integration with the HuggingFace Hub ([#2949])
- Added `ArgillaPeftTrainer` for text and token classificaiton [#2854](https://github.com/argilla-io/argilla/issues/2854)
- Added `predict_proba()` method to `ArgillaSetFitTrainer`
- Added `ArgillaAutoTrainTrainer` for Text Classification [#2664](https://github.com/argilla-io/argilla/issues/2664)
- New `database revisions` command showing database revisions info

[#2615]: https://github.com/argilla-io/argilla/issues/2615

### Fixes

- Avoid rendering html for invalid html strings in Text2text ([#2911]https://github.com/argilla-io/argilla/issues/2911)

### Changed

- The `database migrate` command accepts a `--revision` param to provide specific revision id
- `tokens_length` metrics function returns empty data ([#3045])
- `token_length` metrics function returns empty data ([#3045])
- `mention_length` metrics function returns empty data ([#3045])
- `entity_density` metrics function returns empty data ([#3045])

### Deprecated

- Using Argilla with Python 3.7 runtime is deprecated and support will be removed from version 1.11.0 ([#2902](https://github.com/argilla-io/argilla/issues/2902))
- `tokens_length` metrics function has been deprecated and will be removed in 1.10.0 ([#3045])
- `token_length` metrics function has been deprecated and will be removed in 1.10.0 ([#3045])
- `mention_length` metrics function has been deprecated and will be removed in 1.10.0 ([#3045])
- `entity_density` metrics function has been deprecated and will be removed in 1.10.0 ([#3045])

### Removed

- Removed mention `density`, `tokens_length` and `chars_length` metrics from token classification metrics storage ([#3045])
- Removed token `char_start`, `char_end`, `tag`, and `score` metrics from token classification metrics storage ([#3045])
- Removed tags-related metrics from token classification metrics storage ([#3045])

[#3045]: https://github.com/argilla-io/argilla/pull/3045

## [1.7.0](https://github.com/argilla-io/argilla/compare/v1.6.0...v1.7.0)

### Added

- add `max_retries` and `num_threads` parameters to `rg.log` to run data logging request concurrently with backoff retry policy. See [#2458](https://github.com/argilla-io/argilla/issues/2458) and [#2533](https://github.com/argilla-io/argilla/issues/2533)
- `rg.load` accepts `include_vectors` and `include_metrics` when loading data. Closes [#2398](https://github.com/argilla-io/argilla/issues/2398)
- Added `settings` param to `prepare_for_training` ([#2689](https://github.com/argilla-io/argilla/issues/2689))
- Added `prepare_for_training` for `openai` ([#2658](https://github.com/argilla-io/argilla/issues/2658))
- Added `ArgillaOpenAITrainer` ([#2659](https://github.com/argilla-io/argilla/issues/2659))
- Added `ArgillaSpanMarkerTrainer` for Named Entity Recognition ([#2693](https://github.com/argilla-io/argilla/pull/2693))
- Added `ArgillaTrainer` CLI support. Closes ([#2809](https://github.com/argilla-io/argilla/issues/2809))

### Fixes

- fix image alignment on token classification

### Changed

- Argilla quickstart image dependencies are externalized into `quickstart.requirements.txt`. See [#2666](https://github.com/argilla-io/argilla/pull/2666)
- bulk endpoints will upsert data when record `id` is present. Closes [#2535](https://github.com/argilla-io/argilla/issues/2535)
- moved from `click` to `typer` CLI support. Closes ([#2815](https://github.com/argilla-io/argilla/issues/2815))
- Argilla server docker image is built with PostgreSQL support. Closes [#2686](https://github.com/argilla-io/argilla/issues/2686)
- The `rg.log` computes all batches and raise an error for all failed batches.
- The default batch size for `rg.log` is now 100.

### Fixed

- `argilla.training` bugfixes and unification ([#2665](https://github.com/argilla-io/argilla/issues/2665))
- Resolved several small bugs in the `ArgillaTrainer`.

### Deprecated

- The `rg.log_async` function is deprecated and will be removed in next minor release.

## [1.6.0](https://github.com/argilla-io/argilla/compare/v1.5.1...v1.6.0)

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
- Add user settings page. Closes [#2496](https://github.com/argilla-io/argilla/issues/2496)
- Added `Argilla.training` module with support for `spacy`, `setfit`, and `transformers`. Closes [#2504](https://github.com/argilla-io/argilla/issues/2496)

### Fixes

- Now the `prepare_for_training` method is working when `multi_label=True`. Closes [#2606](https://github.com/argilla-io/argilla/issues/2606)

### Changed

- `ARGILLA_USERS_DB_FILE` environment variable now it's only used to migrate users from YAML file to database ([#2564]).
- `full_name` user field is now deprecated and `first_name` and `last_name` should be used instead ([#2564]).
- `password` user field now requires a minimum of `8` and a maximum of `100` characters in size ([#2564]).
- `quickstart.Dockerfile` image default users from `team` and `argilla` to `admin` and `annotator` including new passwords and API keys ([#2564]).
- Datasets to be managed only by users with `admin` role ([#2564]).
- The list of rules is now accessible while metrics are computed. Closes[#2117](https://github.com/argilla-io/argilla/issues/2117)
- Style updates for weak labeling and adding feedback toast when delete rules. See [#2626](https://github.com/argilla-io/argilla/pull/2626) and [#2648](https://github.com/argilla-io/argilla/pull/2648)

### Removed

- `email` user field ([#2564]).
- `disabled` user field ([#2564]).
- Support for private workspaces ([#2564]).
- `ARGILLA_LOCAL_AUTH_DEFAULT_APIKEY` and `ARGILLA_LOCAL_AUTH_DEFAULT_PASSWORD` environment variables. Use `python -m argilla.tasks.users.create_default` instead ([#2564]).
- The old headers for `API Key` and `workspace` from python client
- The default value for old `API Key` constant. Closes [#2251](https://github.com/argilla-io/argilla/issues/2251)

[#2564]: https://github.com/argilla-io/argilla/issues/2564

## [1.5.1](https://github.com/argilla-io/argilla/compare/v1.5.0...v1.5.1) - 2023-03-30

### Fixes

- Copying datasets between workspaces with proper owner/workspace info. Closes [#2562](https://github.com/argilla-io/argilla/issues/2562)
- Copy dataset with empty workspace to the default user workspace [905d4de](https://github.com/recognai/argilla/commit/905d4deaa769bfc9bbc022cd2dc75c7435cfe865)
- Using elasticsearch config to request backend version. Closes [#2311](https://github.com/argilla-io/argilla/issues/2311)
- Remove sorting by score in labels. Closes [#2622](https://github.com/argilla-io/argilla/issues/2622)

### Changed

- Update field name in metadata for image url. See [#2609](https://github.com/argilla-io/argilla/pull/2609)
- Improvements in tutorial doc cards. Closes [#2216](https://github.com/argilla-io/argilla/issues/2216)

## [1.5.0](https://github.com/argilla-io/argilla/compare/v1.4.0...v1.5.0) - 2023-03-21

### Added

- Add the fields to retrieve when loading the data from argilla. `rg.load` takes too long because of the vector field, even when users don't need it. Closes [#2398](https://github.com/argilla-io/argilla/issues/2398)
- Add new page and components for dataset settings. Closes [#2442](https://github.com/argilla-io/argilla/issues/2003)
- Add ability to show image in records (for TokenClassification and TextClassification) if an URL is passed in metadata with the key \_image_url
- Non-searchable fields support in metadata. [#2570](https://github.com/argilla-io/argilla/pull/2570)
- Add record ID references to the prepare for training methods. Closes [#2483](https://github.com/argilla-io/argilla/issues/2483)
- Add tutorial on Image Classification. [#2420](https://github.com/argilla-io/argilla/pull/2420)
- Add Train button, visible for "admin" role, with code snippets from a selection of libraries. Closes [#2591] (https://github.com/argilla-io/argilla/pull/2591)

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
