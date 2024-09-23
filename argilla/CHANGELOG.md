# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
These are the section headers that we use:
* "Added" for new features.
* "Changed" for changes in existing functionality.
* "Deprecated" for soon-to-be removed features.
* "Removed" for now removed features.
* "Fixed" for any bug fixes.
* "Security" in case of vulnerabilities.
-->

## [Unreleased]()

### Added

- Added `limit` argument when fetching records. ([#5525](https://github.com/argilla-io/argilla/pull/5525)

## [2.2.0](https://github.com/argilla-io/argilla/compare/v2.1.0...v2.2.0)

- Added new `ChatField` supporting chat messages. ([#5376](https://github.com/argilla-io/argilla/pull/5376))
- Added template settings to `rg.Settings` for classification, rating, and ranking questions. ([#5426](https://github.com/argilla-io/argilla/pull/5426))
- Added `rg.Settings` definition based on `datasets.Features` within `rg.Dataset.from_hub`. ([#5426](https://github.com/argilla-io/argilla/pull/5472))
- Added persistent record mapping to `rg.Settings` to be used in `rg.Dataset.records.log`. ([#5466](https://github.com/argilla-io/argilla/pull/5466))
- Added multiple error handling methods to the `rg.Dataset.records.log` method to warn, ignore, or raise errors. ([#5466](https://github.com/argilla-io/argilla/pull/5463))
- Changed dataset import and export of `rg.LabelQuestion` to use `datasets.ClassLabel` not `datasets.Value`. ([#5474](https://github.com/argilla-io/argilla/pull/5474))

## [2.1.0](https://github.com/argilla-io/argilla/compare/v2.0.1...v2.1.0)

### Added

- Added new `ImageField` supporting URLs and Data URLs. ([#5279](https://github.com/argilla-io/argilla/pull/5279))
- Added dark mode ([#5412](https://github.com/argilla-io/argilla/pull/5412))
- Added settings parameter to `rg.Dataset.from_hub` to define the dataset settings before ingesting a dataset from the hub. ([#5418](https://github.com/argilla-io/argilla/pull/5418))

## [2.0.1](https://github.com/argilla-io/argilla/compare/v2.0.0...releases/2.0.1)

### Fixed

- Fixed error when creating optional fields. ([#5362](https://github.com/argilla-io/argilla/pull/5362))
- Fixed error creating integer and float metadata with `visible_for_annotators`. ([#5364](https://github.com/argilla-io/argilla/pull/5364))
- Fixed error when logging records with `suggestions` or `responses` for non-existent questions. ([#5396](https://github.com/argilla-io/argilla/pull/5396) by @maxserras)
- Fixed error from conflicts in testing suite when running tests in parallel. ([#5349](https://github.com/argilla-io/argilla/commit/1119b164d0623170d44561c6b75d439d2dc96bd0))
- Fixed error in response model when creating a response with a `None` value. ([#5343](https://github.com/argilla-io/argilla/commit/9e3705061a2dd88a7852288d9f6fd1aaeaa9b062))

### Changed

- Changed `from_hub` method to raise an error when a dataset with the same name exists. ([#5258](https://github.com/argilla-io/argilla/pull/5358))
- Changed `log` method when ingesting records with no known keys to raise a descriptive error. ([#5356](https://github.com/argilla-io/argilla/pull/5356))
- Changed `code snippets` to add new datasets ([#5395](https://github.com/argilla-io/argilla/pull/5395))

### Added

- Added Google Analytics to the documentation site. ([#5366](https://github.com/argilla-io/argilla/pull/5366))
- Added frontend skeletons to progress metrics to optimise load time and improve user experience. ([#5391](https://github.com/argilla-io/argilla/pull/5391))
- Added documentation in methods in API references for the Python SDK. ([#5400](https://github.com/argilla-io/argilla/commit/a6fc0117bc4923aec0be80df27eb79ddf3f007c7))

### Fixed

- Fix bug when submit the latest record, sometimes you navigate to non existing page [#5419](https://github.com/argilla-io/argilla/pull/5419)

## [2.0.0](https://github.com/argilla-io/argilla/compare/v2.0.0rc1...v2.0.0)

### Added

- Added core class refactors. For an overview, see [this blog post](https://argilla.io/blog/introducing-argilla-new-sdk/)
- Added `TaskDistribution` to define distribution of records to users .
- Added new [documentation site](docs.argilla.io) and structure and migrated [legacy documentation](http://docs.v1.argilla.io/).

### Changed

- Changed `FeedbackDataset` to `Dataset`.
- Changed `rg.init` into `rg.Argilla` class to interact with Argilla server.

### Deprecated

- Deprecated task specific dataset classes like `TextClassification` and `TokenClassification`. To migrate legacy datasets to `rg.Dataset` class, see the [how-to-guide](https://docs.v2.argilla.io/dev/how_to_guides/migrate_from_legacy_datasets/).
- Deprecated use case extensions like `listeners` and `ArgillaTrainer`.

## [2.0.0rc1](https://github.com/argilla-io/argilla/compare/v1.29.0...v2.0.0rc1)

> [!NOTE]
> This release for 2.0.0rc1 does not contain any changelog entries because it is the first release candidate for the 2.0.0 version. The following versions will contain the changelog entries again. For a general overview of the changes in the 2.0.0 version, please refer to [our blog](https://argilla.io/blog/) or [our new documentation](https://docs.argilla.io/latest).

## [1.29.0](https://github.com/argilla-io/argilla/compare/v1.28.0...v1.29.0)

### Added

- Added support for rating questions to include `0` as a valid value. ([#4860](https://github.com/argilla-io/argilla/pull/4860))
- Added support for Python 3.12. ([#4837](https://github.com/argilla-io/argilla/pull/4837))
- Added search by field in the `FeedbackDataset` UI search. ([#4746](https://github.com/argilla-io/argilla/issues/4746))
- Added record metadata info in the `FeedbackDataset` UI. ([#4851](https://github.com/argilla-io/argilla/pull/4851))
- Added highlight on search results in the `FeedbackDataset` UI. ([#4747](https://github.com/argilla-io/argilla/issues/4747))

### Fixed

- Fix wildcard import for the whole argilla module. ([#4874](https://github.com/argilla-io/argilla/pull/4874))
- Fix issue when record does not have vectors related. ([#4856](https://github.com/argilla-io/argilla/pull/4856))
- Fix issue on character level. ([#4836](https://github.com/argilla-io/argilla/pull/4836))

## [1.28.0](https://github.com/argilla-io/argilla/compare/v1.27.0...v1.28.0)

### Added

- Added suggestion multi score attribute. ([#4730](https://github.com/argilla-io/argilla/pull/4730))
- Added order by suggestion first. ([#4731](https://github.com/argilla-io/argilla/pull/4731))
- Added multi selection entity dropdown for span annotation overlap. ([#4735](https://github.com/argilla-io/argilla/pull/4735))
- Added pre selection highlight for span annotation. ([#4726](https://github.com/argilla-io/argilla/pull/4726))
- Added banner when persistent storage is not enabled. ([#4744](https://github.com/argilla-io/argilla/pull/4744))
- Added support on Python SDK for new multi-label questions `labels_order` attribute. ([#4757](https://github.com/argilla-io/argilla/pull/4757))

### Changed

- Changed the way how Hugging Face space and user is showed in sign in. ([#4748](https://github.com/argilla-io/argilla/pull/4748))

### Fixed

- Fixed Korean character reversed. ([#4753](https://github.com/argilla-io/argilla/pull/4753))

### Fixed

- Fixed requirements for version of wrapt library conflicting with Python 3.11 ([#4693](https://github.com/argilla-io/argilla/pull/4693))

## [1.27.0](https://github.com/argilla-io/argilla/compare/v1.26.1...v1.27.0)

### Added

- Added Allow overlap spans in the `FeedbackDataset`. ([#4668](https://github.com/argilla-io/argilla/pull/4668))
- Added `allow_overlapping` parameter for span questions. ([#4697](https://github.com/argilla-io/argilla/pull/4697))
- Added overall progress bar on `Datasets` table. ([#4696](https://github.com/argilla-io/argilla/pull/4696))
- Added German language translation. ([#4688](https://github.com/argilla-io/argilla/pull/4688))

### Changed

- New UI design for suggestions. ([#4682](https://github.com/argilla-io/argilla/pull/4682))

### Fixed

- Improve performance for more than 250 labels. ([#4702](https://github.com/argilla-io/argilla/pull/4702))

## [1.26.1](https://github.com/argilla-io/argilla/compare/v1.26.0...v1.26.1)

### Added

- Added support for automatic detection of RTL languages. ([#4686](https://github.com/argilla-io/argilla/pull/4686))

## [1.26.0](https://github.com/argilla-io/argilla/compare/v1.25.0...v1.26.0)

### Added

- If you expand the labels of a `single or multi` label Question, the state is maintained during the entire annotation process. ([#4630](https://github.com/argilla-io/argilla/pull/4630))
- Added support for span questions in the Python SDK. ([#4617](https://github.com/argilla-io/argilla/pull/4617))
- Added support for span values in suggestions and responses. ([#4623](https://github.com/argilla-io/argilla/pull/4623))
- Added `span` questions for `FeedbackDataset`. ([#4622](https://github.com/argilla-io/argilla/pull/4622))
- Added `ARGILLA_CACHE_DIR` environment variable to configure the client cache directory. ([#4509](https://github.com/argilla-io/argilla/pull/4509))

### Fixed

- Fixed contextualized workspaces. ([#4665](https://github.com/argilla-io/argilla/pull/4665))
- Fixed prepare for training when passing `RankingValueSchema` instances to suggestions. ([#4628](https://github.com/argilla-io/argilla/pull/4628))
- Fixed parsing ranking values in suggestions from HF datasets. ([#4629](https://github.com/argilla-io/argilla/pull/4629))
- Fixed reading description from API response payload. ([#4632](https://github.com/argilla-io/argilla/pull/4632))
- Fixed pulling (n\*chunk_size)+1 records when using `ds.pull` or iterating over the dataset. ([#4662](https://github.com/argilla-io/argilla/pull/4662))
- Fixed client's resolution of enum values when calling the Search and Metrics api, to support Python >=3.11 enum handling. ([#4672](https://github.com/argilla-io/argilla/pull/4672))

## [1.25.0](https://github.com/argilla-io/argilla/compare/v1.24.0...v1.25.0)

> [!NOTE]
> For changes in the argilla-server module, visit the argilla-server [release notes](https://github.com/argilla-io/argilla-server/releases/tag/v1.25.0)

### Added

- Reorder labels in `dataset settings page` for single/multi label questions ([#4598](https://github.com/argilla-io/argilla/pull/4598))
- Added pandas v2 support using the python SDK. ([#4600](https://github.com/argilla-io/argilla/pull/4600))

### Removed

- Removed `missing` response for status filter. Use `pending` instead. ([#4533](https://github.com/argilla-io/argilla/issues/4533))

### Fixed

- Fixed FloatMetadataProperty: value is not a valid float ([#4570](https://github.com/argilla-io/argilla/pull/4605))
- Fixed redirect to `user-settings` instead of 404 `user_settings` ([#4609](https://github.com/argilla-io/argilla/pull/4609))

## [1.24.0](https://github.com/argilla-io/argilla/compare/v1.23.0...v1.24.0)

> [!NOTE]
> This release does not contain any new features, but it includes a major change in the `argilla-server` dependency.
> The package is using the `argilla-server` dependency defined [here](https://github.com/argilla-io/argilla-server). ([#4537](https://github.com/argilla-io/argilla/pull/4537))

### Changed

- The package is using the `argilla-server` dependency defined [here](https://github.com/argilla-io/argilla-server). ([#4537](https://github.com/argilla-io/argilla/pull/4537))

## [1.23.1](https://github.com/argilla-io/argilla/compare/v1.23.0...v1.23.1)

### Fixed

- Fixed Responsive view for Feedback Datasets. ([#4579](https://github.com/argilla-io/argilla/pull/4579))

## [1.23.0](https://github.com/argilla-io/argilla/compare/v1.22.0...v1.23.0)

### Added

- Added bulk annotation by filter criteria. ([#4516](https://github.com/argilla-io/argilla/pull/4516))
- Automatically fetch new datasets on focus tab. ([#4514](https://github.com/argilla-io/argilla/pull/4514))
- API v1 responses returning `Record` schema now always include `dataset_id` as attribute. ([#4482](https://github.com/argilla-io/argilla/pull/4482))
- API v1 responses returning `Response` schema now always include `record_id` as attribute. ([#4482](https://github.com/argilla-io/argilla/pull/4482))
- API v1 responses returning `Question` schema now always include `dataset_id` attribute. ([#4487](https://github.com/argilla-io/argilla/pull/4487))
- API v1 responses returning `Field` schema now always include `dataset_id` attribute. ([#4488](https://github.com/argilla-io/argilla/pull/4488))
- API v1 responses returning `MetadataProperty` schema now always include `dataset_id` attribute. ([#4489](https://github.com/argilla-io/argilla/pull/4489))
- API v1 responses returning `VectorSettings` schema now always include `dataset_id` attribute. ([#4490](https://github.com/argilla-io/argilla/pull/4490))
- Added `pdf_to_html` function to `.html_utils` module that convert PDFs to dataURL to be able to render them in tha Argilla UI. ([#4481](https://github.com/argilla-io/argilla/issues/4481#issuecomment-1903695755))
- Added `ARGILLA_AUTH_SECRET_KEY` environment variable. ([#4539](https://github.com/argilla-io/argilla/pull/4539))
- Added `ARGILLA_AUTH_ALGORITHM` environment variable. ([#4539](https://github.com/argilla-io/argilla/pull/4539))
- Added `ARGILLA_AUTH_TOKEN_EXPIRATION` environment variable. ([#4539](https://github.com/argilla-io/argilla/pull/4539))
- Added `ARGILLA_AUTH_OAUTH_CFG` environment variable. ([#4546](https://github.com/argilla-io/argilla/pull/4546))
- Added OAuth2 support for HuggingFace Hub. ([#4546](https://github.com/argilla-io/argilla/pull/4546))

### Deprecated

- Deprecated `ARGILLA_LOCAL_AUTH_*` environment variables. Will be removed in the release v1.25.0. ([#4539](https://github.com/argilla-io/argilla/pull/4539))

### Changed

- Changed regex pattern for `username` attribute in `UserCreate`. Now uppercase letters are allowed. ([#4544](https://github.com/argilla-io/argilla/pull/4544))

### Removed

- Remove sending `Authorization` header from python SDK requests. ([#4535](https://github.com/argilla-io/argilla/pull/4535))

### Fixed

- Fixed keyboard shortcut for label questions. ([#4530](https://github.com/argilla-io/argilla/pull/4530))

## [1.22.0](https://github.com/argilla-io/argilla/compare/v1.21.0...v1.22.0)

### Added

- Added Bulk annotation support. ([#4333](https://github.com/argilla-io/argilla/pull/4333))
- Restore filters from feedback dataset settings. ([#4461])(https://github.com/argilla-io/argilla/pull/4461)
- Warning on feedback dataset settings when leaving page with unsaved changes. ([#4461](https://github.com/argilla-io/argilla/pull/4461))
- Added pydantic v2 support using the python SDK. ([#4459](https://github.com/argilla-io/argilla/pull/4459))
- Added `vector_settings` to the `__repr__` method of the `FeedbackDataset` and `RemoteFeedbackDataset`. ([#4454](https://github.com/argilla-io/argilla/pull/4454))
- Added integration for `sentence-transformers` using `SentenceTransformersExtractor` to configure `vector_settings` in `FeedbackDataset` and `FeedbackRecord`. ([#4454](https://github.com/argilla-io/argilla/pull/4454))

### Changed

- Module `argilla.cli.server` definitions have been moved to `argilla.server.cli` module. ([#4472](https://github.com/argilla-io/argilla/pull/4472))
- [breaking] Changed `vector_settings_by_name` for generic `property_by_name` usage, which will return `None` instead of raising an error. ([#4454](https://github.com/argilla-io/argilla/pull/4454))
- The constant definition `ES_INDEX_REGEX_PATTERN` in module `argilla._constants` is now private. ([#4472](https://github.com/argilla-io/argilla/pull/4474))
- `nan` values in metadata properties will raise a 422 error when creating/updating records. ([#4300](https://github.com/argilla-io/argilla/issues/4300))
- `None` values are now allowed in metadata properties. ([#4300](https://github.com/argilla-io/argilla/issues/4300))
- Refactor and add `width`, `height`, `autoplay` and `loop` attributes as optional args in `to_html` functions. ([#4481](https://github.com/argilla-io/argilla/issues/4481#issuecomment-1903695755))

### Fixed

- Paginating to a new record, automatically scrolls down to selected form area. ([#4333](https://github.com/argilla-io/argilla/pull/4333))

### Deprecated

- The `missing` response status for filtering records is deprecated and will be removed in the release v1.24.0. Use `pending` instead. ([#4433](https://github.com/argilla-io/argilla/pull/4433))

### Removed

- The deprecated `python -m argilla database` command has been removed. ([#4472](https://github.com/argilla-io/argilla/pull/4472))

## [1.21.0](https://github.com/argilla-io/argilla/compare/v1.20.0...v1.21.0)

### Added

- Added new draft queue for annotation view ([#4334](https://github.com/argilla-io/argilla/pull/4334))
- Added annotation metrics module for the `FeedbackDataset` (`argilla.client.feedback.metrics`). ([#4175](https://github.com/argilla-io/argilla/pull/4175)).
- Added strategy to handle and translate errors from the server for `401` HTTP status code` ([#4362](https://github.com/argilla-io/argilla/pull/4362))
- Added integration for `textdescriptives` using `TextDescriptivesExtractor` to configure `metadata_properties` in `FeedbackDataset` and `FeedbackRecord`. ([#4400](https://github.com/argilla-io/argilla/pull/4400)). Contributed by @m-newhauser
- Added `POST /api/v1/me/responses/bulk` endpoint to create responses in bulk for current user. ([#4380](https://github.com/argilla-io/argilla/pull/4380))
- Added list support for term metadata properties. (Closes [#4359](https://github.com/argilla-io/argilla/issues/4359))
- Added new CLI task to reindex datasets and records into the search engine. ([#4404](https://github.com/argilla-io/argilla/pull/4404))
- Added `httpx_extra_kwargs` argument to `rg.init` and `Argilla` to allow passing extra arguments to `httpx.Client` used by `Argilla`. ([#4440](https://github.com/argilla-io/argilla/pull/4441))
- Added `ResponseStatusFilter` enum in `__init__` imports of Argilla ([#4118](https://github.com/argilla-io/argilla/pull/4463)). Contributed by @Piyush-Kumar-Ghosh.

### Changed

- More productive and simpler shortcut system ([#4215](https://github.com/argilla-io/argilla/pull/4215))
- Move `ArgillaSingleton`, `init` and `active_client` to a new module `singleton`. ([#4347](https://github.com/argilla-io/argilla/pull/4347))
- Updated `argilla.load` functions to also work with `FeedbackDataset`s. ([#4347](https://github.com/argilla-io/argilla/pull/4347))
- [breaking] Updated `argilla.delete` functions to also work with `FeedbackDataset`s. It now raises an error if the dataset does not exist. ([#4347](https://github.com/argilla-io/argilla/pull/4347))
- Updated `argilla.list_datasets` functions to also work with `FeedbackDataset`s. ([#4347](https://github.com/argilla-io/argilla/pull/4347))

### Fixed

- Fixed error in `TextClassificationSettings.from_dict` method in which the `label_schema` created was a list of `dict` instead of a list of `str`. ([#4347](https://github.com/argilla-io/argilla/pull/4347))
- Fixed total records on pagination component ([#4424](https://github.com/argilla-io/argilla/pull/4424))

### Removed

- Removed `draft` auto save for annotation view ([#4334](https://github.com/argilla-io/argilla/pull/4334))

## [1.20.0](https://github.com/argilla-io/argilla/compare/v1.19.0...v1.20.0)

### Added

- Added `GET /api/v1/datasets/:dataset_id/records/search/suggestions/options` endpoint to return suggestion available options for searching. ([#4260](https://github.com/argilla-io/argilla/pull/4260))
- Added `metadata_properties` to the `__repr__` method of the `FeedbackDataset` and `RemoteFeedbackDataset`.([#4192](https://github.com/argilla-io/argilla/pull/4192)).
- Added `get_model_kwargs`, `get_trainer_kwargs`, `get_trainer_model`, `get_trainer_tokenizer` and `get_trainer` -methods to the `ArgillaTrainer` to improve interoperability across frameworks. ([#4214](https://github.com/argilla-io/argilla/pull/4214)).
- Added additional formatting checks to the `ArgillaTrainer` to allow for better interoperability of `defaults` and `formatting_func` usage. ([#4214](https://github.com/argilla-io/argilla/pull/4214)).
- Added a warning to the `update_config`-method of `ArgillaTrainer` to emphasize if the `kwargs` were updated correctly. ([#4214](https://github.com/argilla-io/argilla/pull/4214)).
- Added `argilla.client.feedback.utils` module with `html_utils` (this mainly includes `video/audio/image_to_html` that convert media to dataURL to be able to render them in tha Argilla UI and `create_token_highlights` to highlight tokens in a custom way. Both work on TextQuestion and TextField with use_markdown=True) and `assignments` (this mainly includes `assign_records` to assign records according to a number of annotators and records, an overlap and the shuffle option; and `assign_workspace` to assign and create if needed a workspace according to the record assignment). ([#4121](https://github.com/argilla-io/argilla/pull/4121))

### Fixed

- Fixed error in `ArgillaTrainer`, with numerical labels, using `RatingQuestion` instead of `RankingQuestion` ([#4171](https://github.com/argilla-io/argilla/pull/4171))
- Fixed error in `ArgillaTrainer`, now we can train for `extractive_question_answering` using a validation sample ([#4204](https://github.com/argilla-io/argilla/pull/4204))
- Fixed error in `ArgillaTrainer`, when training for `sentence-similarity` it didn't work with a list of values per record ([#4211](https://github.com/argilla-io/argilla/pull/4211))
- Fixed error in the unification strategy for `RankingQuestion` ([#4295](https://github.com/argilla-io/argilla/pull/4295))
- Fixed `TextClassificationSettings.labels_schema` order was not being preserved. Closes [#3828](https://github.com/argilla-io/argilla/issues/3828) ([#4332](https://github.com/argilla-io/argilla/pull/4332))
- Fixed error when requesting non-existing API endpoints. Closes [#4073](https://github.com/argilla-io/argilla/issues/4073) ([#4325](https://github.com/argilla-io/argilla/pull/4325))
- Fixed error when passing `draft` responses to create records endpoint. ([#4354](https://github.com/argilla-io/argilla/pull/4354))

### Changed

- [breaking] Suggestions `agent` field only accepts now some specific characters and a limited length. ([#4265](https://github.com/argilla-io/argilla/pull/4265))
- [breaking] Suggestions `score` field only accepts now float values in the range `0` to `1`. ([#4266](https://github.com/argilla-io/argilla/pull/4266))
- Updated `POST /api/v1/dataset/:dataset_id/records/search` endpoint to support optional `query` attribute. ([#4327](https://github.com/argilla-io/argilla/pull/4327))
- Updated `POST /api/v1/dataset/:dataset_id/records/search` endpoint to support `filter` and `sort` attributes. ([#4327](https://github.com/argilla-io/argilla/pull/4327))
- Updated `POST /api/v1/me/datasets/:dataset_id/records/search` endpoint to support optional `query` attribute. ([#4270](https://github.com/argilla-io/argilla/pull/4270))
- Updated `POST /api/v1/me/datasets/:dataset_id/records/search` endpoint to support `filter` and `sort` attributes. ([#4270](https://github.com/argilla-io/argilla/pull/4270))
- Changed the logging style while pulling and pushing `FeedbackDataset` to Argilla from `tqdm` style to `rich`. ([#4267](https://github.com/argilla-io/argilla/pull/4267)). Contributed by @zucchini-nlp.
- Updated `push_to_argilla` to print `repr` of the pushed `RemoteFeedbackDataset` after push and changed `show_progress` to True by default. ([#4223](https://github.com/argilla-io/argilla/pull/4223))
- Changed `models` and `tokenizer` for the `ArgillaTrainer` to explicitly allow for changing them when needed. ([#4214](https://github.com/argilla-io/argilla/pull/4214)).

## [1.19.0](https://github.com/argilla-io/argilla/compare/v1.18.0...v1.19.0)

### Added

- Added `POST /api/v1/datasets/:dataset_id/records/search` endpoint to search for records without user context, including responses by all users. ([#4143](https://github.com/argilla-io/argilla/pull/4143))
- Added `POST /api/v1/datasets/:dataset_id/vectors-settings` endpoint for creating vector settings for a dataset. ([#3776](https://github.com/argilla-io/argilla/pull/3776))
- Added `GET /api/v1/datasets/:dataset_id/vectors-settings` endpoint for listing the vectors settings for a dataset. ([#3776](https://github.com/argilla-io/argilla/pull/3776))
- Added `DELETE /api/v1/vectors-settings/:vector_settings_id` endpoint for deleting a vector settings. ([#3776](https://github.com/argilla-io/argilla/pull/3776))
- Added `PATCH /api/v1/vectors-settings/:vector_settings_id` endpoint for updating a vector settings. ([#4092](https://github.com/argilla-io/argilla/pull/4092))
- Added `GET /api/v1/records/:record_id` endpoint to get a specific record. ([#4039](https://github.com/argilla-io/argilla/pull/4039))
- Added support to include vectors for `GET /api/v1/datasets/:dataset_id/records` endpoint response using `include` query param. ([#4063](https://github.com/argilla-io/argilla/pull/4063))
- Added support to include vectors for `GET /api/v1/me/datasets/:dataset_id/records` endpoint response using `include` query param. ([#4063](https://github.com/argilla-io/argilla/pull/4063))
- Added support to include vectors for `POST /api/v1/me/datasets/:dataset_id/records/search` endpoint response using `include` query param. ([#4063](https://github.com/argilla-io/argilla/pull/4063))
- Added `show_progress` argument to `from_huggingface()` method to make the progress bar for parsing records process optional.([#4132](https://github.com/argilla-io/argilla/pull/4132)).
- Added a progress bar for parsing records process to `from_huggingface()` method with `trange` in `tqdm`.([#4132](https://github.com/argilla-io/argilla/pull/4132)).
- Added to sort by `inserted_at` or `updated_at` for datasets with no metadata. ([4147](https://github.com/argilla-io/argilla/pull/4147))
- Added `max_records` argument to `pull()` method for `RemoteFeedbackDataset`.([#4074](https://github.com/argilla-io/argilla/pull/4074))
- Added functionality to push your models to the Hugging Face hub with `ArgillaTrainer.push_to_huggingface` ([#3976](https://github.com/argilla-io/argilla/pull/3976)). Contributed by @Racso-3141.
- Added `filter_by` argument to `ArgillaTrainer` to filter by `response_status` ([#4120](https://github.com/argilla-io/argilla/pull/4120)).
- Added `sort_by` argument to `ArgillaTrainer` to sort by `metadata` ([#4120](https://github.com/argilla-io/argilla/pull/4120)).
- Added `max_records` argument to `ArgillaTrainer` to limit record used for training ([#4120](https://github.com/argilla-io/argilla/pull/4120)).
- Added `add_vector_settings` method to local and remote `FeedbackDataset`. ([#4055](https://github.com/argilla-io/argilla/pull/4055))
- Added `update_vectors_settings` method to local and remote `FeedbackDataset`. ([#4122](https://github.com/argilla-io/argilla/pull/4122))
- Added `delete_vectors_settings` method to local and remote `FeedbackDataset`. ([#4130](https://github.com/argilla-io/argilla/pull/4130))
- Added `vector_settings_by_name` method to local and remote `FeedbackDataset`. ([#4055](https://github.com/argilla-io/argilla/pull/4055))
- Added `find_similar_records` method to local and remote `FeedbackDataset`. ([#4023](https://github.com/argilla-io/argilla/pull/4023))
- Added `ARGILLA_SEARCH_ENGINE` environment variable to configure the search engine to use. ([#4019](https://github.com/argilla-io/argilla/pull/4019))

### Changed

- [breaking] Remove support for Elasticsearch < 8.5 and OpenSearch < 2.4. ([#4173](https://github.com/argilla-io/argilla/pull/4173))
- [breaking] Users working with OpenSearch engines must use version >=2.4 and set `ARGILLA_SEARCH_ENGINE=opensearch`. ([#4019](https://github.com/argilla-io/argilla/pull/4019) and [#4111](https://github.com/argilla-io/argilla/pull/4111))
- [breaking] Changed `FeedbackDataset.*_by_name()` methods to return `None` when no match is found ([#4101](https://github.com/argilla-io/argilla/pull/3976)).
- [breaking] `limit` query parameter for `GET /api/v1/datasets/:dataset_id/records` endpoint is now only accepting values greater or equal than `1` and less or equal than `1000`. ([#4143](https://github.com/argilla-io/argilla/pull/4143))
- [breaking] `limit` query parameter for `GET /api/v1/me/datasets/:dataset_id/records` endpoint is now only accepting values greater or equal than `1` and less or equal than `1000`. ([#4143](https://github.com/argilla-io/argilla/pull/4143))
- Update `GET /api/v1/datasets/:dataset_id/records` endpoint to fetch record using the search engine. ([#4142](https://github.com/argilla-io/argilla/pull/4142))
- Update `GET /api/v1/me/datasets/:dataset_id/records` endpoint to fetch record using the search engine. ([#4142](https://github.com/argilla-io/argilla/pull/4142))
- Update `POST /api/v1/datasets/:dataset_id/records` endpoint to allow to create records with `vectors` ([#4022](https://github.com/argilla-io/argilla/pull/4022))
- Update `PATCH /api/v1/datasets/:dataset_id` endpoint to allow updating `allow_extra_metadata` attribute. ([#4112](https://github.com/argilla-io/argilla/pull/4112))
- Update `PATCH /api/v1/datasets/:dataset_id/records` endpoint to allow to update records with `vectors`. ([#4062](https://github.com/argilla-io/argilla/pull/4062))
- Update `PATCH /api/v1/records/:record_id` endpoint to allow to update record with `vectors`. ([#4062](https://github.com/argilla-io/argilla/pull/4062))
- Update `POST /api/v1/me/datasets/:dataset_id/records/search` endpoint to allow to search records with vectors. ([#4019](https://github.com/argilla-io/argilla/pull/4019))
- Update `BaseElasticAndOpenSearchEngine.index_records` method to also index record vectors. ([#4062](https://github.com/argilla-io/argilla/pull/4062))
- Update `FeedbackDataset.__init__` to allow passing a list of vector settings. ([#4055](https://github.com/argilla-io/argilla/pull/4055))
- Update `FeedbackDataset.push_to_argilla` to also push vector settings. ([#4055](https://github.com/argilla-io/argilla/pull/4055))
- Update `FeedbackDatasetRecord` to support the creation of records with vectors. ([#4043](https://github.com/argilla-io/argilla/pull/4043))
- Using cosine similarity to compute similarity between vectors. ([#4124](https://github.com/argilla-io/argilla/pull/4124))

### Fixed

- Fixed svg images out of screen with too large images ([#4047](https://github.com/argilla-io/argilla/pull/4047))
- Fixed creating records with responses from multiple users. Closes [#3746](https://github.com/argilla-io/argilla/issues/3746) and [#3808](https://github.com/argilla-io/argilla/issues/3808) ([#4142](https://github.com/argilla-io/argilla/pull/4142))
- Fixed deleting or updating responses as an owner for annotators. (Commit [403a66d](https://github.com/argilla-io/argilla/commit/403a66d16d816fa8a62e3f76314ccc90e0073297))
- Fixed passing user_id when getting records by id. (Commit [98c7927](https://github.com/argilla-io/argilla/commit/98c792757a21da05bac89b7f625e7e5792ad59f9))
- Fixed non-basic tags serialized when pushing a dataset to the Hugging Face Hub. Closes [#4089](https://github.com/argilla-io/argilla/issues/4089) ([#4200](https://github.com/argilla-io/argilla/pull/4200))

## [1.18.0](https://github.com/argilla-io/argilla/compare/v1.17.0...v1.18.0)

### Added

- New `GET /api/v1/datasets/:dataset_id/metadata-properties` endpoint for listing dataset metadata properties. ([#3813](https://github.com/argilla-io/argilla/pull/3813))
- New `POST /api/v1/datasets/:dataset_id/metadata-properties` endpoint for creating dataset metadata properties. ([#3813](https://github.com/argilla-io/argilla/pull/3813))
- New `PATCH /api/v1/metadata-properties/:metadata_property_id` endpoint allowing the update of a specific metadata property. ([#3952](https://github.com/argilla-io/argilla/pull/3952))
- New `DELETE /api/v1/metadata-properties/:metadata_property_id` endpoint for deletion of a specific metadata property. ([#3911](https://github.com/argilla-io/argilla/pull/3911))
- New `GET /api/v1/metadata-properties/:metadata_property_id/metrics` endpoint to compute metrics for a specific metadata property. ([#3856](https://github.com/argilla-io/argilla/pull/3856))
- New `PATCH /api/v1/records/:record_id` endpoint to update a record. ([#3920](https://github.com/argilla-io/argilla/pull/3920))
- New `PATCH /api/v1/dataset/:dataset_id/records` endpoint to bulk update the records of a dataset. ([#3934](https://github.com/argilla-io/argilla/pull/3934))
- Missing validations to `PATCH /api/v1/questions/:question_id`. Now `title` and `description` are using the same validations used to create questions. ([#3967](https://github.com/argilla-io/argilla/pull/3967))
- Added `TermsMetadataProperty`, `IntegerMetadataProperty` and `FloatMetadataProperty` classes allowing to define metadata properties for a `FeedbackDataset`. ([#3818](https://github.com/argilla-io/argilla/pull/3818))
- Added `metadata_filters` to `filter_by` method in `RemoteFeedbackDataset` to filter based on metadata i.e. `TermsMetadataFilter`, `IntegerMetadataFilter`, and `FloatMetadataFilter`. ([#3834](https://github.com/argilla-io/argilla/pull/3834))
- Added a validation layer for both `metadata_properties` and `metadata_filters` in their schemas and as part of the `add_records` and `filter_by` methods, respectively. ([#3860](https://github.com/argilla-io/argilla/pull/3860))
- Added `sort_by` query parameter to listing records endpoints that allows to sort the records by `inserted_at`, `updated_at` or metadata property. ([#3843](https://github.com/argilla-io/argilla/pull/3843))
- Added `add_metadata_property` method to both `FeedbackDataset` and `RemoteFeedbackDataset` (i.e. `FeedbackDataset` in Argilla). ([#3900](https://github.com/argilla-io/argilla/pull/3900))
- Added fields `inserted_at` and `updated_at` in `RemoteResponseSchema`. ([#3822](https://github.com/argilla-io/argilla/pull/3822))
- Added support for `sort_by` for `RemoteFeedbackDataset` i.e. a `FeedbackDataset` uploaded to Argilla. ([#3925](https://github.com/argilla-io/argilla/pull/3925))
- Added `metadata_properties` support for both `push_to_huggingface` and `from_huggingface`. ([#3947](https://github.com/argilla-io/argilla/pull/3947))
- Add support for update records (`metadata`) from Python SDK. ([#3946](https://github.com/argilla-io/argilla/pull/3946))
- Added `delete_metadata_properties` method to delete metadata properties. ([#3932](https://github.com/argilla-io/argilla/pull/3932))
- Added `update_metadata_properties` method to update `metadata_properties`. ([#3961](https://github.com/argilla-io/argilla/pull/3961))
- Added automatic model card generation through `ArgillaTrainer.save` ([#3857](https://github.com/argilla-io/argilla/pull/3857))
- Added `FeedbackDataset` `TaskTemplateMixin` for pre-defined task templates. ([#3969](https://github.com/argilla-io/argilla/pull/3969))
- A maximum limit of 50 on the number of options a ranking question can accept. ([#3975](https://github.com/argilla-io/argilla/pull/3975))
- New `last_activity_at` field to `FeedbackDataset` exposing when the last activity for the associated dataset occurs. ([#3992](https://github.com/argilla-io/argilla/pull/3992))

### Changed

- `GET /api/v1/datasets/{dataset_id}/records`, `GET /api/v1/me/datasets/{dataset_id}/records` and `POST /api/v1/me/datasets/{dataset_id}/records/search` endpoints to return the `total` number of records. ([#3848](https://github.com/argilla-io/argilla/pull/3848), [#3903](https://github.com/argilla-io/argilla/pull/3903))
- Implemented `__len__` method for filtered datasets to return the number of records matching the provided filters. ([#3916](https://github.com/argilla-io/argilla/pull/3916))
- Increase the default max result window for Elasticsearch created for Feedback datasets. ([#3929](https://github.com/argilla-io/argilla/pull/))
- Force elastic index refresh after records creation. ([#3929](https://github.com/argilla-io/argilla/pull/))
- Validate metadata fields for filtering and sorting in the Python SDK. ([#3993](https://github.com/argilla-io/argilla/pull/3993))
- Using metadata property name instead of id for indexing data in search engine index. ([#3994](https://github.com/argilla-io/argilla/pull/3994))

### Fixed

- Fixed response schemas to allow `values` to be `None` i.e. when a record is discarded the `response.values` are set to `None`. ([#3926](https://github.com/argilla-io/argilla/pull/3926))

## [1.17.0](https://github.com/argilla-io/argilla/compare/v1.16.0...v1.17.0)

### Added

- Added fields `inserted_at` and `updated_at` in `RemoteResponseSchema` ([#3822](https://github.com/argilla-io/argilla/pull/3822)).
- Added automatic model card generation through `ArgillaTrainer.save` ([#3857](https://github.com/argilla-io/argilla/pull/3857)).
- Added task templates to the `FeedbackDataset` ([#3973](https://github.com/argilla-io/argilla/pull/3973)).

### Changed

- Updated `Dockerfile` to use multi stage build ([#3221](https://github.com/argilla-io/argilla/pull/3221) and [#3793](https://github.com/argilla-io/argilla/pull/3793)).
- Updated active learning for text classification notebooks to use the most recent small-text version ([#3831](https://github.com/argilla-io/argilla/pull/3831)).
- Changed argilla dataset name in the active learning for text classification notebooks to be consistent with the default names in the huggingface spaces ([#3831](https://github.com/argilla-io/argilla/pull/3831)).
- FeedbackDataset API methods have been aligned to be accessible through the several implementations ([#3937](https://github.com/argilla-io/argilla/pull/3937)).
- The `unify_responses` support for remote datasets ([#3937](https://github.com/argilla-io/argilla/pull/3937)).

### Fixed

- Fix field not shown in the order defined in the dataset settings. Closes [#3959](https://github.com/argilla-io/argilla/issues/3959) ([#3984](https://github.com/argilla-io/argilla/pull/3984))
- Updated active learning for text classification notebooks to pass ids of type int to `TextClassificationRecord` ([#3831](https://github.com/argilla-io/argilla/pull/3831)).
- Fixed record fields validation that was preventing from logging records with optional fields (i.e. `required=True`) when the field value was `None` ([#3846](https://github.com/argilla-io/argilla/pull/3846)).
- Always set `pretrained_model_name_or_path` attribute as string in `ArgillaTrainer` ([#3914](https://github.com/argilla-io/argilla/pull/3914)).
- The `inserted_at` and `updated_at` attributes are create using the `utcnow` factory to avoid unexpected race conditions on timestamp creation ([#3945](https://github.com/argilla-io/argilla/pull/3945))
- Fixed `configure_dataset_settings` when providing the workspace via the arg `workspace` ([#3887](https://github.com/argilla-io/argilla/pull/3887)).
- Fixed saving of models trained with `ArgillaTrainer` with a `peft_config` parameter ([#3795](https://github.com/argilla-io/argilla/pull/3795)).
- Fixed backwards compatibility on `from_huggingface` when loading a `FeedbackDataset` from the Hugging Face Hub that was previously dumped using another version of Argilla, starting at 1.8.0, when it was first introduced ([#3829](https://github.com/argilla-io/argilla/pull/3829)).
- Fixed wrong `__repr__` problem for `TrainingTask`. ([#3969](https://github.com/argilla-io/argilla/pull/3969))
- Fixed wrong key return error `prepare_for_training_with_*` for `TrainingTask`. ([#3969](https://github.com/argilla-io/argilla/pull/3969))

### Deprecated

- Function `rg.configure_dataset` is deprecated in favour of `rg.configure_dataset_settings`. The former will be removed in version 1.19.0

## [1.16.0](https://github.com/argilla-io/argilla/compare/v1.15.1...v1.16.0)

### Added

- Added `ArgillaTrainer` integration with sentence-transformers, allowing fine tuning for sentence similarity ([#3739](https://github.com/argilla-io/argilla/pull/3739))
- Added `ArgillaTrainer` integration with `TrainingTask.for_question_answering` ([#3740](https://github.com/argilla-io/argilla/pull/3740))
- Added `Auto save record` to save automatically the current record that you are working on ([#3541](https://github.com/argilla-io/argilla/pull/3541))
- Added `ArgillaTrainer` integration with OpenAI, allowing fine tuning for chat completion ([#3615](https://github.com/argilla-io/argilla/pull/3615))
- Added `workspaces list` command to list Argilla workspaces ([#3594](https://github.com/argilla-io/argilla/pull/3594)).
- Added `datasets list` command to list Argilla datasets ([#3658](https://github.com/argilla-io/argilla/pull/3658)).
- Added `users create` command to create users ([#3667](https://github.com/argilla-io/argilla/pull/3667)).
- Added `whoami` command to get current user ([#3673](https://github.com/argilla-io/argilla/pull/3673)).
- Added `users delete` command to delete users ([#3671](https://github.com/argilla-io/argilla/pull/3671)).
- Added `users list` command to list users ([#3688](https://github.com/argilla-io/argilla/pull/3688)).
- Added `workspaces delete-user` command to remove a user from a workspace ([#3699](https://github.com/argilla-io/argilla/pull/3699)).
- Added `datasets list` command to list Argilla datasets ([#3658](https://github.com/argilla-io/argilla/pull/3658)).
- Added `users create` command to create users ([#3667](https://github.com/argilla-io/argilla/pull/3667)).
- Added `users delete` command to delete users ([#3671](https://github.com/argilla-io/argilla/pull/3671)).
- Added `workspaces create` command to create an Argilla workspace ([#3676](https://github.com/argilla-io/argilla/pull/3676)).
- Added `datasets push-to-hub` command to push a `FeedbackDataset` from Argilla into the HuggingFace Hub ([#3685](https://github.com/argilla-io/argilla/pull/3685)).
- Added `info` command to get info about the used Argilla client and server ([#3707](https://github.com/argilla-io/argilla/pull/3707)).
- Added `datasets delete` command to delete a `FeedbackDataset` from Argilla ([#3703](https://github.com/argilla-io/argilla/pull/3703)).
- Added `created_at` and `updated_at` properties to `RemoteFeedbackDataset` and `FilteredRemoteFeedbackDataset` ([#3709](https://github.com/argilla-io/argilla/pull/3709)).
- Added handling `PermissionError` when executing a command with a logged in user with not enough permissions ([#3717](https://github.com/argilla-io/argilla/pull/3717)).
- Added `workspaces add-user` command to add a user to workspace ([#3712](https://github.com/argilla-io/argilla/pull/3712)).
- Added `workspace_id` param to `GET /api/v1/me/datasets` endpoint ([#3727](https://github.com/argilla-io/argilla/pull/3727)).
- Added `workspace_id` arg to `list_datasets` in the Python SDK ([#3727](https://github.com/argilla-io/argilla/pull/3727)).
- Added `argilla` script that allows to execute Argilla CLI using the `argilla` command ([#3730](https://github.com/argilla-io/argilla/pull/3730)).
- Added support for passing already initialized `model` and `tokenizer` instances to the `ArgillaTrainer` ([#3751](https://github.com/argilla-io/argilla/pull/3751))
- Added `server_info` function to check the Argilla server information (also accessible via `rg.server_info`) ([#3772](https://github.com/argilla-io/argilla/issues/3772)).

### Changed

- Move `database` commands under `server` group of commands ([#3710](https://github.com/argilla-io/argilla/pull/3710))
- `server` commands only included in the CLI app when `server` extra requirements are installed ([#3710](https://github.com/argilla-io/argilla/pull/3710)).
- Updated `PUT /api/v1/responses/{response_id}` to replace `values` stored with received `values` in request ([#3711](https://github.com/argilla-io/argilla/pull/3711)).
- Display a `UserWarning` when the `user_id` in `Workspace.add_user` and `Workspace.delete_user` is the ID of an user with the owner role as they don't require explicit permissions ([#3716](https://github.com/argilla-io/argilla/issues/3716)).
- Rename `tasks` sub-package to `cli` ([#3723](https://github.com/argilla-io/argilla/pull/3723)).
- Changed `argilla database` command in the CLI to now be accessed via `argilla server database`, to be deprecated in the upcoming release ([#3754](https://github.com/argilla-io/argilla/pull/3754)).
- Changed `visible_options` (of label and multi label selection questions) validation in the backend to check that the provided value is greater or equal than/to 3 and less or equal than/to the number of provided options ([#3773](https://github.com/argilla-io/argilla/pull/3773)).

### Fixed

- Fixed `remove user modification in text component on clear answers` ([#3775](https://github.com/argilla-io/argilla/pull/3775))
- Fixed `Highlight raw text field in dataset feedback task` ([#3731](https://github.com/argilla-io/argilla/pull/3731))
- Fixed `Field title too long` ([#3734](https://github.com/argilla-io/argilla/pull/3734))
- Fixed error messages when deleting a `DatasetForTextClassification` ([#3652](https://github.com/argilla-io/argilla/pull/3652))
- Fixed `Pending queue` pagination problems when during data annotation ([#3677](https://github.com/argilla-io/argilla/pull/3677))
- Fixed `visible_labels` default value to be 20 just when `visible_labels` not provided and `len(labels) > 20`, otherwise it will either be the provided `visible_labels` value or `None`, for `LabelQuestion` and `MultiLabelQuestion` ([#3702](https://github.com/argilla-io/argilla/pull/3702)).
- Fixed `DatasetCard` generation when `RemoteFeedbackDataset` contains suggestions ([#3718](https://github.com/argilla-io/argilla/pull/3718)).
- Add missing `draft` status in `ResponseSchema` as now there can be responses with `draft` status when annotating via the UI ([#3749](https://github.com/argilla-io/argilla/pull/3749)).
- Searches when queried words are distributed along the record fields ([#3759](https://github.com/argilla-io/argilla/pull/3759)).
- Fixed Python 3.11 compatibility issue with `/api/datasets` endpoints due to the `TaskType` enum replacement in the endpoint URL ([#3769](https://github.com/argilla-io/argilla/pull/3769)).
- Fixed `RankingValueSchema` and `FeedbackRankingValueModel` schemas to allow `rank=None` when `status=draft` ([#3781](https://github.com/argilla-io/argilla/pull/3781)).

## [1.15.1](https://github.com/argilla-io/argilla/compare/v1.15.0...v1.15.1)

### Fixed

- Fixed `Text component` text content sanitization behavior just for markdown to prevent disappear the text([#3738](https://github.com/argilla-io/argilla/pull/3738))
- Fixed `Text component` now you need to press Escape to exit the text area ([#3733](https://github.com/argilla-io/argilla/pull/3733))
- Fixed `SearchEngine` was creating the same number of primary shards and replica shards for each `FeedbackDataset` ([#3736](https://github.com/argilla-io/argilla/pull/3736)).

## [1.15.0](https://github.com/argilla-io/argilla/compare/v1.14.1...v1.15.0)

### Added

- Added `Enable to update guidelines and dataset settings for Feedback Datasets directly in the UI` ([#3489](https://github.com/argilla-io/argilla/pull/3489))
- Added `ArgillaTrainer` integration with TRL, allowing for easy supervised finetuning, reward modeling, direct preference optimization and proximal policy optimization ([#3467](https://github.com/argilla-io/argilla/pull/3467))
- Added `formatting_func` to `ArgillaTrainer` for `FeedbackDataset` datasets add a custom formatting for the data ([#3599](https://github.com/argilla-io/argilla/pull/3599)).
- Added `login` function in `argilla.client.login` to login into an Argilla server and store the credentials locally ([#3582](https://github.com/argilla-io/argilla/pull/3582)).
- Added `login` command to login into an Argilla server ([#3600](https://github.com/argilla-io/argilla/pull/3600)).
- Added `logout` command to logout from an Argilla server ([#3605](https://github.com/argilla-io/argilla/pull/3605)).
- Added `DELETE /api/v1/suggestions/{suggestion_id}` endpoint to delete a suggestion given its ID ([#3617](https://github.com/argilla-io/argilla/pull/3617)).
- Added `DELETE /api/v1/records/{record_id}/suggestions` endpoint to delete several suggestions linked to the same record given their IDs ([#3617](https://github.com/argilla-io/argilla/pull/3617)).
- Added `response_status` param to `GET /api/v1/datasets/{dataset_id}/records` to be able to filter by `response_status` as previously included for `GET /api/v1/me/datasets/{dataset_id}/records` ([#3613](https://github.com/argilla-io/argilla/pull/3613)).
- Added `list` classmethod to `ArgillaMixin` to be used as `FeedbackDataset.list()`, also including the `workspace` to list from as arg ([#3619](https://github.com/argilla-io/argilla/pull/3619)).
- Added `filter_by` method in `RemoteFeedbackDataset` to filter based on `response_status` ([#3610](https://github.com/argilla-io/argilla/pull/3610)).
- Added `list_workspaces` function (to be used as `rg.list_workspaces`, but `Workspace.list` is preferred) to list all the workspaces from an user in Argilla ([#3641](https://github.com/argilla-io/argilla/pull/3641)).
- Added `list_datasets` function (to be used as `rg.list_datasets`) to list the `TextClassification`, `TokenClassification`, and `Text2Text` datasets in Argilla ([#3638](https://github.com/argilla-io/argilla/pull/3638)).
- Added `RemoteSuggestionSchema` to manage suggestions in Argilla, including the `delete` method to delete suggestios from Argilla via `DELETE /api/v1/suggestions/{suggestion_id}` ([#3651](https://github.com/argilla-io/argilla/pull/3651)).
- Added `delete_suggestions` to `RemoteFeedbackRecord` to remove suggestions from Argilla via `DELETE /api/v1/records/{record_id}/suggestions` ([#3651](https://github.com/argilla-io/argilla/pull/3651)).

### Changed

- Changed `Optional label for * mark for required question` ([#3608](https://github.com/argilla-io/argilla/pull/3608))
- Updated `RemoteFeedbackDataset.delete_records` to use batch delete records endpoint ([#3580](https://github.com/argilla-io/argilla/pull/3580)).
- Included `allowed_for_roles` for some `RemoteFeedbackDataset`, `RemoteFeedbackRecords`, and `RemoteFeedbackRecord` methods that are only allowed for users with roles `owner` and `admin` ([#3601](https://github.com/argilla-io/argilla/pull/3601)).
- Renamed `ArgillaToFromMixin` to `ArgillaMixin` ([#3619](https://github.com/argilla-io/argilla/pull/3619)).
- Move `users` CLI app under `database` CLI app ([#3593](https://github.com/argilla-io/argilla/pull/3593)).
- Move server `Enum` classes to `argilla.server.enums` module ([#3620](https://github.com/argilla-io/argilla/pull/3620)).

### Fixed

- Fixed `Filter by workspace in breadcrumbs` ([#3577](https://github.com/argilla-io/argilla/pull/3577))
- Fixed `Filter by workspace in datasets table` ([#3604](https://github.com/argilla-io/argilla/pull/3604))
- Fixed `Query search highlight` for Text2Text and TextClassification ([#3621](https://github.com/argilla-io/argilla/pull/3621))
- Fixed `RatingQuestion.values` validation to raise a `ValidationError` when values are out of range i.e. [1, 10] ([#3626](https://github.com/argilla-io/argilla/pull/3626)).

### Removed

- Removed `multi_task_text_token_classification` from `TaskType` as not used ([#3640](https://github.com/argilla-io/argilla/pull/3640)).
- Removed `argilla_id` in favor of `id` from `RemoteFeedbackDataset` ([#3663](https://github.com/argilla-io/argilla/pull/3663)).
- Removed `fetch_records` from `RemoteFeedbackDataset` as now the records are lazily fetched from Argilla ([#3663](https://github.com/argilla-io/argilla/pull/3663)).
- Removed `push_to_argilla` from `RemoteFeedbackDataset`, as it just works when calling it through a `FeedbackDataset` locally, as now the updates of the remote datasets are automatically pushed to Argilla ([#3663](https://github.com/argilla-io/argilla/pull/3663)).
- Removed `set_suggestions` in favor of `update(suggestions=...)` for both `FeedbackRecord` and `RemoteFeedbackRecord`, as all the updates of any "updateable" attribute of a record will go through `update` instead ([#3663](https://github.com/argilla-io/argilla/pull/3663)).
- Remove unused `owner` attribute for client Dataset data model ([#3665](https://github.com/argilla-io/argilla/pull/3665))

## [1.14.1](https://github.com/argilla-io/argilla/compare/v1.14.0...v1.14.1)

### Fixed

- Fixed PostgreSQL database not being updated after `begin_nested` because of missing `commit` ([#3567](https://github.com/argilla-io/argilla/pull/3567)).

### Fixed

- Fixed `settings` could not be provided when updating a `rating` or `ranking` question ([#3552](https://github.com/argilla-io/argilla/pull/3552)).

## [1.14.0](https://github.com/argilla-io/argilla/compare/v1.13.3...v1.14.0)

### Added

- Added `PATCH /api/v1/fields/{field_id}` endpoint to update the field title and markdown settings ([#3421](https://github.com/argilla-io/argilla/pull/3421)).
- Added `PATCH /api/v1/datasets/{dataset_id}` endpoint to update dataset name and guidelines ([#3402](https://github.com/argilla-io/argilla/pull/3402)).
- Added `PATCH /api/v1/questions/{question_id}` endpoint to update question title, description and some settings (depending on the type of question) ([#3477](https://github.com/argilla-io/argilla/pull/3477)).
- Added `DELETE /api/v1/records/{record_id}` endpoint to remove a record given its ID ([#3337](https://github.com/argilla-io/argilla/pull/3337)).
- Added `pull` method in `RemoteFeedbackDataset` (a `FeedbackDataset` pushed to Argilla) to pull all the records from it and return it as a local copy as a `FeedbackDataset` ([#3465](https://github.com/argilla-io/argilla/pull/3465)).
- Added `delete` method in `RemoteFeedbackDataset` (a `FeedbackDataset` pushed to Argilla) ([#3512](https://github.com/argilla-io/argilla/pull/3512)).
- Added `delete_records` method in `RemoteFeedbackDataset`, and `delete` method in `RemoteFeedbackRecord` to delete records from Argilla ([#3526](https://github.com/argilla-io/argilla/pull/3526)).

### Changed

- Improved efficiency of weak labeling when dataset contains vectors ([#3444](https://github.com/argilla-io/argilla/pull/3444)).
- Added `ArgillaDatasetMixin` to detach the Argilla-related functionality from the `FeedbackDataset` ([#3427](https://github.com/argilla-io/argilla/pull/3427))
- Moved `FeedbackDataset`-related `pydantic.BaseModel` schemas to `argilla.client.feedback.schemas` instead, to be better structured and more scalable and maintainable ([#3427](https://github.com/argilla-io/argilla/pull/3427))
- Update CLI to use database async connection ([#3450](https://github.com/argilla-io/argilla/pull/3450)).
- Limit rating questions values to the positive range [1, 10] ([#3451](https://github.com/argilla-io/argilla/issues/3451)).
- Updated `POST /api/users` endpoint to be able to provide a list of workspace names to which the user should be linked to ([#3462](https://github.com/argilla-io/argilla/pull/3462)).
- Updated Python client `User.create` method to be able to provide a list of workspace names to which the user should be linked to ([#3462](https://github.com/argilla-io/argilla/pull/3462)).
- Updated `GET /api/v1/me/datasets/{dataset_id}/records` endpoint to allow getting records matching one of the response statuses provided via query param ([#3359](https://github.com/argilla-io/argilla/pull/3359)).
- Updated `POST /api/v1/me/datasets/{dataset_id}/records` endpoint to allow searching records matching one of the response statuses provided via query param ([#3359](https://github.com/argilla-io/argilla/pull/3359)).
- Updated `SearchEngine.search` method to allow searching records matching one of the response statuses provided ([#3359](https://github.com/argilla-io/argilla/pull/3359)).
- After calling `FeedbackDataset.push_to_argilla`, the methods `FeedbackDataset.add_records` and `FeedbackRecord.set_suggestions` will automatically call Argilla with no need of calling `push_to_argilla` explicitly ([#3465](https://github.com/argilla-io/argilla/pull/3465)).
- Now calling `FeedbackDataset.push_to_huggingface` dumps the `responses` as a `List[Dict[str, Any]]` instead of `Sequence` to make it more readable via 🤗`datasets` ([#3539](https://github.com/argilla-io/argilla/pull/3539)).

### Fixed

- Fixed issue with `bool` values and `default` from Jinja2 while generating the HuggingFace `DatasetCard` from `argilla_template.md` ([#3499](https://github.com/argilla-io/argilla/pull/3499)).
- Fixed `DatasetConfig.from_yaml` which was failing when calling `FeedbackDataset.from_huggingface` as the UUIDs cannot be deserialized automatically by `PyYAML`, so UUIDs are neither dumped nor loaded anymore ([#3502](https://github.com/argilla-io/argilla/pull/3502)).
- Fixed an issue that didn't allow the Argilla server to work behind a proxy ([#3543](https://github.com/argilla-io/argilla/pull/3543)).
- `TextClassificationSettings` and `TokenClassificationSettings` labels are properly parsed to strings both in the Python client and in the backend endpoint ([#3495](https://github.com/argilla-io/argilla/issues/3495)).
- Fixed `PUT /api/v1/datasets/{dataset_id}/publish` to check whether at least one field and question has `required=True` ([#3511](https://github.com/argilla-io/argilla/pull/3511)).
- Fixed `FeedbackDataset.from_huggingface` as `suggestions` were being lost when there were no `responses` ([#3539](https://github.com/argilla-io/argilla/pull/3539)).
- Fixed `QuestionSchema` and `FieldSchema` not validating `name` attribute ([#3550](https://github.com/argilla-io/argilla/pull/3550)).

### Deprecated

- After calling `FeedbackDataset.push_to_argilla`, calling `push_to_argilla` again won't do anything since the dataset is already pushed to Argilla ([#3465](https://github.com/argilla-io/argilla/pull/3465)).
- After calling `FeedbackDataset.push_to_argilla`, calling `fetch_records` won't do anything since the records are lazily fetched from Argilla ([#3465](https://github.com/argilla-io/argilla/pull/3465)).
- After calling `FeedbackDataset.push_to_argilla`, the Argilla ID is no longer stored in the attribute/property `argilla_id` but in `id` instead ([#3465](https://github.com/argilla-io/argilla/pull/3465)).

## [1.13.3](https://github.com/argilla-io/argilla/compare/v1.13.2...v1.13.3)

### Fixed

- Fixed `ModuleNotFoundError` caused because the `argilla.utils.telemetry` module used in the `ArgillaTrainer` was importing an optional dependency not installed by default ([#3471](https://github.com/argilla-io/argilla/pull/3471)).
- Fixed `ImportError` caused because the `argilla.client.feedback.config` module was importing `pyyaml` optional dependency not installed by default ([#3471](https://github.com/argilla-io/argilla/pull/3471)).

## [1.13.2](https://github.com/argilla-io/argilla/compare/v1.13.1...v1.13.2)

### Fixed

- The `suggestion_type_enum` ENUM data type created in PostgreSQL didn't have any value ([#3445](https://github.com/argilla-io/argilla/pull/3445)).

## [1.13.1](https://github.com/argilla-io/argilla/compare/v1.13.0...v1.13.1)

### Fixed

- Fix database migration for PostgreSQL (See [#3438](https://github.com/argilla-io/argilla/pull/3438))

## [1.13.0](https://github.com/argilla-io/argilla/compare/v1.12.1...v1.13.0)

### Added

- Added `GET /api/v1/users/{user_id}/workspaces` endpoint to list the workspaces to which a user belongs ([#3308](https://github.com/argilla-io/argilla/pull/3308) and [#3343](https://github.com/argilla-io/argilla/pull/3343)).
- Added `HuggingFaceDatasetMixin` for internal usage, to detach the `FeedbackDataset` integrations from the class itself, and use Mixins instead ([#3326](https://github.com/argilla-io/argilla/pull/3326)).
- Added `GET /api/v1/records/{record_id}/suggestions` API endpoint to get the list of suggestions for the responses associated to a record ([#3304](https://github.com/argilla-io/argilla/pull/3304)).
- Added `POST /api/v1/records/{record_id}/suggestions` API endpoint to create a suggestion for a response associated to a record ([#3304](https://github.com/argilla-io/argilla/pull/3304)).
- Added support for `RankingQuestionStrategy`, `RankingQuestionUnification` and the `.for_text_classification` method for the `TrainingTaskMapping` ([#3364](https://github.com/argilla-io/argilla/pull/3364))
- Added `PUT /api/v1/records/{record_id}/suggestions` API endpoint to create or update a suggestion for a response associated to a record ([#3304](https://github.com/argilla-io/argilla/pull/3304) & [3391](https://github.com/argilla-io/argilla/pull/3391)).
- Added `suggestions` attribute to `FeedbackRecord`, and allow adding and retrieving suggestions from the Python client ([#3370](https://github.com/argilla-io/argilla/pull/3370))
- Added `allowed_for_roles` Python decorator to check whether the current user has the required role to access the decorated function/method for `User` and `Workspace` ([#3383](https://github.com/argilla-io/argilla/pull/3383))
- Added API and Python Client support for workspace deletion (Closes [#3260](https://github.com/argilla-io/argilla/issues/3260))
- Added `GET /api/v1/me/workspaces` endpoint to list the workspaces of the current active user ([#3390](https://github.com/argilla-io/argilla/pull/3390))

### Changed

- Updated output payload for `GET /api/v1/datasets/{dataset_id}/records`, `GET /api/v1/me/datasets/{dataset_id}/records`, `POST /api/v1/me/datasets/{dataset_id}/records/search` endpoints to include the suggestions of the records based on the value of the `include` query parameter ([#3304](https://github.com/argilla-io/argilla/pull/3304)).
- Updated `POST /api/v1/datasets/{dataset_id}/records` input payload to add suggestions ([#3304](https://github.com/argilla-io/argilla/pull/3304)).
- The `POST /api/datasets/:dataset-id/:task/bulk` endpoints don't create the dataset if does not exists (Closes [#3244](https://github.com/argilla-io/argilla/issues/3244))
- Added Telemetry support for `ArgillaTrainer` (closes [#3325](https://github.com/argilla-io/argilla/issues/3325))
- `User.workspaces` is no longer an attribute but a property, and is calling `list_user_workspaces` to list all the workspace names for a given user ID ([#3334](https://github.com/argilla-io/argilla/pull/3334))
- Renamed `FeedbackDatasetConfig` to `DatasetConfig` and export/import from YAML as default instead of JSON (just used internally on `push_to_huggingface` and `from_huggingface` methods of `FeedbackDataset`) ([#3326](https://github.com/argilla-io/argilla/pull/3326)).
- The protected metadata fields support other than textual info - existing datasets must be reindex. See [docs](https://docs.v1.argilla.io/en/latest/getting_started/installation/configurations/database_migrations.html#elasticsearch) for more detail (Closes [#3332](https://github.com/argilla-io/argilla/issues/3332)).
- Updated `Dockerfile` parent image from `python:3.9.16-slim` to `python:3.10.12-slim` ([#3425](https://github.com/argilla-io/argilla/pull/3425)).
- Updated `quickstart.Dockerfile` parent image from `elasticsearch:8.5.3` to `argilla/argilla-server:${ARGILLA_VERSION}` ([#3425](https://github.com/argilla-io/argilla/pull/3425)).

### Removed

- Removed support to non-prefixed environment variables. All valid env vars start with `ARGILLA_` (See [#3392](https://github.com/argilla-io/argilla/pull/3392)).

### Fixed

- Fixed `GET /api/v1/me/datasets/{dataset_id}/records` endpoint returning always the responses for the records even if `responses` was not provided via the `include` query parameter ([#3304](https://github.com/argilla-io/argilla/pull/3304)).
- Values for protected metadata fields are not truncated (Closes [#3331](https://github.com/argilla-io/argilla/issues/3331)).
- Big number ids are properly rendered in UI (Closes [#3265](https://github.com/argilla-io/argilla/issues/3265))
- Fixed `ArgillaDatasetCard` to include the values/labels for all the existing questions ([#3366](https://github.com/argilla-io/argilla/pull/3265))

### Deprecated

- Integer support for record id in text classification, token classification and text2text datasets.

## [1.12.1](https://github.com/argilla-io/argilla/compare/v1.12.0...v1.12.1)

### Fixed

- Using `rg.init` with default `argilla` user skips setting the default workspace if not available. (Closes [#3340](https://github.com/argilla-io/argilla/issues/3340))
- Resolved wrong import structure for `ArgillaTrainer` and `TrainingTaskMapping` (Closes [#3345](https://github.com/argilla-io/argilla/issues/3345))
- Pin pydantic dependency to version < 2 (Closes [3348](https://github.com/argilla-io/argilla/issues/3348))

## [1.12.0](https://github.com/argilla-io/argilla/compare/v1.11.0...v1.12.0)

### Added

- Added `RankingQuestionSettings` class allowing to create ranking questions in the API using `POST /api/v1/datasets/{dataset_id}/questions` endpoint ([#3232](https://github.com/argilla-io/argilla/pull/3232))
- Added `RankingQuestion` in the Python client to create ranking questions ([#3275](https://github.com/argilla-io/argilla/issues/3275)).
- Added `Ranking` component in feedback task question form ([#3177](https://github.com/argilla-io/argilla/pull/3177) & [#3246](https://github.com/argilla-io/argilla/pull/3246)).
- Added `FeedbackDataset.prepare_for_training` method for generaring a framework-specific dataset with the responses provided for `RatingQuestion`, `LabelQuestion` and `MultiLabelQuestion` ([#3151](https://github.com/argilla-io/argilla/pull/3151)).
- Added `ArgillaSpaCyTransformersTrainer` class for supporting the training with `spacy-transformers` ([#3256](https://github.com/argilla-io/argilla/pull/3256)).

#### Docs

- Added instructions for how to run the Argilla frontend in the developer docs ([#3314](https://github.com/argilla-io/argilla/pull/3314)).

### Changed

- All docker related files have been moved into the `docker` folder ([#3053](https://github.com/argilla-io/argilla/pull/3053)).
- `release.Dockerfile` have been renamed to `Dockerfile` ([#3133](https://github.com/argilla-io/argilla/pull/3133)).
- Updated `rg.load` function to raise a `ValueError` with a explanatory message for the cases in which the user tries to use the function to load a `FeedbackDataset` ([#3289](https://github.com/argilla-io/argilla/pull/3289)).
- Updated `ArgillaSpaCyTrainer` to allow re-using `tok2vec` ([#3256](https://github.com/argilla-io/argilla/pull/3256)).

### Fixed

- Check available workspaces on Argilla on `rg.set_workspace` (Closes [#3262](https://github.com/argilla-io/argilla/issues/3262))

## [1.11.0](https://github.com/argilla-io/argilla/compare/v1.10.0...v1.11.0)

### Fixed

- Replaced `np.float` alias by `float` to avoid `AttributeError` when using `find_label_errors` function with `numpy>=1.24.0` ([#3214](https://github.com/argilla-io/argilla/pull/3214)).
- Fixed `format_as("datasets")` when no responses or optional respones in `FeedbackRecord`, to set their value to what 🤗 Datasets expects instead of just `None` ([#3224](https://github.com/argilla-io/argilla/pull/3224)).
- Fixed `push_to_huggingface()` when `generate_card=True` (default behaviour), as we were passing a sample record to the `ArgillaDatasetCard` class, and `UUID`s introduced in 1.10.0 ([#3192](https://github.com/argilla-io/argilla/pull/3192)), are not JSON-serializable ([#3231](https://github.com/argilla-io/argilla/pull/3231)).
- Fixed `from_argilla` and `push_to_argilla` to ensure consistency on both field and question re-construction, and to ensure `UUID`s are properly serialized as `str`, respectively ([#3234](https://github.com/argilla-io/argilla/pull/3234)).
- Refactored usage of `import argilla as rg` to clarify package navigation ([#3279](https://github.com/argilla-io/argilla/pull/3279)).

#### Docs

- Fixed URLs in Weak Supervision with Sentence Tranformers tutorial [#3243](https://github.com/argilla-io/argilla/pull/3243).
- Fixed library buttons' formatting on Tutorials page ([#3255](https://github.com/argilla-io/argilla/pull/3255)).
- Modified styling of error code outputs in notebooks ([#3270](https://github.com/argilla-io/argilla/pull/3270)).
- Added ElasticSearch and OpenSearch versions ([#3280](https://github.com/argilla-io/argilla/pull/3280)).
- Removed template notebook from table of contents ([#3271](https://github.com/argilla-io/argilla/pull/3271)).
- Fixed tutorials with `pip install argilla` to not use older versions of the package ([#3282](https://github.com/argilla-io/argilla/pull/3282)).

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

#### Docs

- Resolved typos in the docs ([#3240](https://github.com/argilla-io/argilla/pull/3240)).
- Fixed mention of master branch ([#3254](https://github.com/argilla-io/argilla/pull/3254)).

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
- Added the information about executing tests in the developer documentation ([#3143]).

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
