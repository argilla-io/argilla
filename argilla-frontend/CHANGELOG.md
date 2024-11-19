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

- Add a high-contrast theme & improvements for the forced-colors mode. ([#5661](https://github.com/argilla-io/argilla/pull/5661))
- Add English as the default language and add language selector in the user settings page. ([#5690](https://github.com/argilla-io/argilla/pull/5690))

### Fixed

- Fixed highlighting on same record ([#5693](https://github.com/argilla-io/argilla/pull/5693))

## [2.4.1](https://github.com/argilla-io/argilla/compare/v2.4.0...v2.4.1)

### Added

- Added redirect to error page when repoId is invalid ([#5670](https://github.com/argilla-io/argilla/pull/5670))

### Fixed

- Fixed redirection problems after users sign-in using HF OAuth. ([#5635](https://github.com/argilla-io/argilla/pull/5635))
- Fixed highlighting of the searched text in text, span and chat fields ([#5678](https://github.com/argilla-io/argilla/pull/5678))
- Fixed validation for rating question when creating a dataset ([#5670](https://github.com/argilla-io/argilla/pull/5670))
- Fixed question name based on question type when creating a dataset ([#5670](https://github.com/argilla-io/argilla/pull/5670))

## [2.4.0](https://github.com/argilla-io/argilla/compare/v2.3.0...v2.4.0)

### Added

- Added new dataset configurator to import datasets from Hugging Face using Argilla UI. ([#5532](https://github.com/argilla-io/argilla/pull/5532))
- Improve Accessibility for Screenreaders ([#5634](https://github.com/argilla-io/argilla/pull/5634))

### Fixed

- Refine German translations and update non-localized UI elements. ([#5632](https://github.com/argilla-io/argilla/pull/5632))

## [2.3.0](https://github.com/argilla-io/argilla/compare/v2.2.0...v2.3.0)

### Added

- Added new field `CustomField`. ([#5462](https://github.com/argilla-io/argilla/pull/5462))

### Fixed

- Fix autofill form on sign-in page. ([#5522](https://github.com/argilla-io/argilla/pull/5522))
- Support copy on clipboard for no secure context. ([#5535](https://github.com/argilla-io/argilla/pull/5535))

## [2.2.0](https://github.com/argilla-io/argilla/compare/v2.1.0...v2.2.0)

### Added

- Added `Required/Optional` label on `Field dataset settings tab` and `Question dataset settings tab`. ([#5394](https://github.com/argilla-io/argilla/pull/5394))
- Added new `ChatField`. ([#5376](https://github.com/argilla-io/argilla/pull/5376))

## [2.1.0](https://github.com/argilla-io/argilla/compare/v2.0.1...v2.1.0)

### Added

- Added `DarkMode` ([#5412](https://github.com/argilla-io/argilla/pull/5412))
- Added new `empty queue messages` ([#5403](https://github.com/argilla-io/argilla/pull/5403))
- Added `HTML Sandbox` to support external and custom CSS and Javascript in fields ([#5353](https://github.com/argilla-io/argilla/pull/5353))
- Added `Spanish` languages ([#5416](https://github.com/argilla-io/argilla/pull/5416))
- Added new `ImageField` supporting URLs and Data URLs. ([#5279](https://github.com/argilla-io/argilla/pull/5279))

> [!NOTE]
> For older versions, please review the argilla/CHANGELOG.md and argilla-server/CHANGELOG.md files.
