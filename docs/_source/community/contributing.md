# Contributor Documentation <!-- omit in toc -->

Thank you for investing your time in contributing to our project! Any contribution you make will be reflected in our most recent version of [Argilla](https://github.com/argilla-io/argilla) 🤩.

Read our [Code of Conduct](https://github.com/argilla-io/argilla/blob/develop/CODE_OF_CONDUCT.md) to keep our community approachable and respectable.

In this guide you will get an overview of the contribution workflow from opening an issue, creating a PR, reviewing, and merging the PR.

## New contributor guide

To get an overview of the project, read our [README](https://github.com/argilla-io/argilla/blob/develop/README.md). Here are some resources to help you get started with open source contributions:

- [Finding good first issue](https://github.com/argilla-io/argilla/labels/good%20first%20issue)
- [Find and review pull requests](https://github.com/argilla-io/argilla/pulls)
- [Setting up the Argilla developer environment](./developer_docs.rst)
- [Write a tutorial](https://github.com/argilla-io/argilla/issues/2030)
- [Schedule a meeting with our developer advocate](https://calendly.com/argilla-office-hours/meeting-with-david-from-argilla-30m)

## Getting started

To navigate our codebase with confidence, see [our Python client code](https://docs.argilla.io/en/latest/reference/python/index.html) 🐍. For more information on how to use our UI, see [our web app reference](https://docs.argilla.io/en/latest/reference/webapp/index.html) 💻.

We accept three kinds of contributions.
- [documentation](#features-and-documentation): better textual support for features. Best to get started.
- [issues](#issues): bug reports that directly fix something that is broken. Generally smaller in nature.
- [features](#features-and-documentation): new functionalities. Generally larger in nature.

### Issues

#### Create a new issue

If you spot a problem with the docs or our code, [search if an issue already exists](https://github.com/argilla-io/argilla/issues?q=is%3Aissue). If a related issue doesn't exist, you can open a new issue using a relevant [issue form](https://github.com/argilla-io/argilla/issues/new?assignees=&labels=bug&template=bug_report.md&title=). Try to fill out the entire template to ensure it is clear what the issue entails and it is reproducible for other users.

#### Solve an issue

Scan through our [existing issues](https://github.com/argilla-io/argilla/issues?q=is%3Aissue) to find one that interests you. You can narrow down the [search using `labels`](https://github.com/argilla-io/argilla/labels) as filters. If you find an issue to work on, you are welcome to [create a fork and start making changes](#make-changes). However, we always advise you to ask for some input within the discussion on the issue, or by contacting us via Slack or by [scheduling a meeting](https://calendly.com/argilla-office-hours/meeting-with-david-from-argilla-30m).

### Features and documentation

We are always looking for [new tutorials](https://github.com/argilla-io/argilla/issues/2030)!

#### Create a new feature

If you feel something can be enhanced, [search if the feature already exists](https://github.com/argilla-io/argilla/issues?q=is%3Aissue+label%3Aenhancement).  If a related feature doesn't exist, you can open a new feature using a relevant [feature form](https://github.com/argilla-io/argilla/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=). Try to fill out the entire template to ensure it is clear what the issue entails and it is reproducible for other users. For documentation, assign the label `documentation` too.

#### Solve an existing feature

Scan through our [existing issues](https://github.com/argilla-io/argilla/issues?q=is%3Aissue+label%3Aenhancement) to find one that interests you. You can narrow down the [search using `labels`](https://github.com/argilla-io/argilla/labels) as filters. If you find a feature to work on, you are welcome to [create a fork and start making changes](#make-changes). However, we always advise you to ask for some input within the discussion on the issue, or by contacting us via Slack or by [scheduling a meeting](https://calendly.com/argilla-office-hours/meeting-with-david-from-argilla-30m).

### Make Changes

- Create [a fork](https://github.com/argilla-io/argilla/fork) of our `development` branch.
  - Note, for updates solely to the documentation, you are allowed to work in the `main` branch.
- To start working on code changes, we suggest, you take a look at our tutorial on setting up the [development environment](./developer_docs.rst).
- Work on your awesome contribution and adhere to our formatting guidelines.
  - Don´t forget to also check if:
    - Your update requires updates to our docs.
    - Your update and fork are mentioned in the original issue or feature.
- Finally, open a [PR](#pull-request) with a fix.

### Pull Request

When you're finished with the changes, create a pull request, also known as a PR.
- [Open a PR in the Argilla repo](https://github.com/argilla-io/argilla/compare).
- Fill the PR template so that we can review your PR. This template helps reviewers understand your changes as well as the purpose of your pull request.
- Don't forget to link PR to issue within the template next to the "Closes #" in the template.
- Enable the checkbox to allow maintainer edits so the branch can be updated for a merge.
Once you submit your PR, a team member will review your proposal. We may ask questions or request additional information.
- We may ask for changes to be made before a PR can be merged, either using [suggested changes](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/incorporating-feedback-in-your-pull-request) or pull request comments. You can apply suggested changes directly through the UI. You can make any other changes in your fork, then commit them to your branch.
- As you update your PR and apply changes, mark each conversation as [resolved](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/commenting-on-a-pull-request#resolving-conversations).
- If you run into any merge issues, checkout this [git tutorial](https://github.com/skills/resolve-merge-conflicts) to help you resolve merge conflicts and other issues.

### Your PR is merged!

Congratulations 🎉🎊 We thank you 🫡

Once your PR is merged, your contributions will be publicly visible on the [Argilla GitHub](https://github.com/argilla-io/argilla#contributors).

Additionally, we will include your changes in the next release based on our [development branch](https://github.com/argilla-io/argilla/tree/develop).

We will probably contact you, but if you would like to send your personal information (LinkedIn, profile picture, GitHub) to david@argilla.io, he can set everything up for receiving your JustDiggit bunds and a LinkedIn shoutout.

