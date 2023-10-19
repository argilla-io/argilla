import typing


if typing.TYPE_CHECKING:
    from argilla.client.feedback.dataset.base import FeedbackDatasetBase


def validate_metadata_names(dataset: "FeedbackDatasetBase", names: typing.List[str]) -> None:
    """Validates that the metadata names used in the filters are valid."""

    metadata_property_names = {metadata_property.name: True for metadata_property in dataset.metadata_properties}

    if not metadata_property_names:
        return

    for name in set(names):
        if not metadata_property_names.get(name):
            raise ValueError(
                f"The metadata property name `{name}` does not exist in the current `FeedbackDataset` in Argilla."
                f" The existing metadata properties names are: {list(metadata_property_names.keys())}."
            )
