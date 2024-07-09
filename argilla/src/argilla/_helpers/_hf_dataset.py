from typing import Optional, Type


def resolve_hf_datasets_type() -> Optional[Type["HFDataset"]]:
    """This function resolves the `datasets.Dataset` type safely in case the datasets package is not installed.

    Returns:
        Optional[Type]: The Dataset class definition in case the datasets package is installed. Otherwise, None.
    """
    try:
        from datasets import Dataset

        return Dataset
    except ImportError:
        return None
