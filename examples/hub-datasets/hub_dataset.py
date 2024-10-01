import logging
import warnings
from functools import lru_cache
from typing import Iterable, List

import httpx


class HubDataset:
    """
    A class to interact with the Hugging Face Datasets Hub API.
    """

    _LOGGER = logging.getLogger("dataset.viewer")

    _BASE_URL = "https://datasets-server.huggingface.co/"

    def __init__(
        self,
        dataset: str,
        config: str | None = None,
        split: str | None = None,
        httpx_client_args: dict | None = None,
        **kwargs,
    ):
        """
        Initialize the class with the dataset, config, and split to use.


        Arguments:
            dataset (str): The dataset to use.
            config (str, optional): The config of the dataset to use. Defaults to None.
            split (str, optional): The split of the dataset to use. Defaults to None.
            httpx_client_args (dict, optional): Additional arguments to pass to the httpx.Client. Defaults to None.
            **kwargs: Additional parameters to pass to the API calls as query parameters.

        """

        self.client = httpx.Client(
            base_url=self._BASE_URL,
            timeout=30,
            **(httpx_client_args or {}),
        )

        self._batch_size = 100
        self.__params = {
            "dataset": dataset,
            "config": config,
            "split": split,
            **kwargs,
        }

        if config is None:
            self.__params["config"] = self._resolve_config()

        if split is None:
            self.__params["split"] = self._resolve_split()

    @property
    def dataset(self):
        """The dataset to use"""
        return self.__params["dataset"]

    @property
    def config(self):
        """The config of the dataset to use"""

        config = self.__params["config"]
        if config is None:
            config = self._resolve_config()
            self.__params["config"] = config
        return config

    @property
    def split(self):
        """The split of the dataset to use"""

        split = self.__params["split"]
        if split is None:
            split = self._resolve_split()
            self.__params["split"] = split
        return split

    def features(self) -> List[dict]:
        """The features of the dataset"""
        info = self.info()
        return info.get("features")

    def get(self, row_idx: int) -> dict:
        """Get a single row by its index"""

        offset = self._page_offset_for_row_id(row_idx)
        offset_idx = row_idx - offset
        result = self.rows(offset=offset)
        return result["rows"][offset_idx]

    @lru_cache
    def is_valid(self):
        """https://redocly.github.io/redoc/?url=https://datasets-server.huggingface.co/openapi.json#operation/isValidDataset"""
        response = self.client.get(f"/is-valid", params=self.__params)
        self._raise_for_status(response)

        return response.json()

    @lru_cache
    def info(self):
        """https://redocly.github.io/redoc/?url=https://datasets-server.huggingface.co/openapi.json#operation/getInfo"""
        response = self.client.get("/info", params=self.__params)
        self._raise_for_status(response)

        return response.json()["dataset_info"]

    @lru_cache
    def size(self):
        """https://redocly.github.io/redoc/?url=https://datasets-server.huggingface.co/openapi.json#operation/getSize"""
        response = self.client.get("/size", params=self.__params)
        self._raise_for_status(response)

        splits = response.json()["size"]["splits"]

        for split in splits:
            if split["split"] == self.split:
                return split

        warnings.warn(f"Split {self.split} not found in {splits}")

    @lru_cache
    def statistics(self):
        """https://redocly.github.io/redoc/?url=https://datasets-server.huggingface.co/openapi.json#operation/getStatistics"""
        response = self.client.get("/statistics", params=self.__params)
        self._raise_for_status(response)

        return response.json()["statistics"]

    @lru_cache
    def rows(self, **kwargs):
        """https://redocly.github.io/redoc/?url=https://datasets-server.huggingface.co/openapi.json#operation/listRows"""
        length = kwargs.pop("length", self._batch_size)

        response = self.client.get(
            f"/rows",
            params={**self.__params, "length": length, **kwargs},
        )
        self._raise_for_status(response)
        json_data = response.json()
        json_data.pop("features")

        return json_data

    @lru_cache
    def search(self, *, query: str, **kwargs):
        """https://redocly.github.io/redoc/?url=https://datasets-server.huggingface.co/openapi.json#operation/searchRows"""
        length = kwargs.pop("length", self._batch_size)

        response = self.client.get(
            f"/search",
            params={**self.__params, "query": query, "length": length, **kwargs},
        )
        self._raise_for_status(response)
        json_data = response.json()
        json_data.pop("features")

        return json_data

    @lru_cache
    def filter(self, *, where: str, **kwargs):
        """https://redocly.github.io/redoc/?url=https://datasets-server.huggingface.co/openapi.json#operation/filterRows"""
        length = kwargs.pop("length", self._batch_size)

        response = self.client.get(
            f"/filter",
            params={**self.__params, "where": where, "length": length, **kwargs},
        )
        self._raise_for_status(response)
        json_data = response.json()
        json_data.pop("features")

        return json_data

    @lru_cache
    def splits(self):
        """https://redocly.github.io/redoc/?url=https://datasets-server.huggingface.co/openapi.json#operation/listSplits"""
        response = self.client.get("/splits", params=self.__params)
        self._raise_for_status(response)

        return response.json()["splits"]

    @lru_cache
    def parquet_files(self):
        """https://redocly.github.io/redoc/?url=https://datasets-server.huggingface.co/openapi.json#operation/listParquetFiles"""

        response = self.client.get("/parquet", params=self.__params)
        self._raise_for_status(response)

        return response.json()["parquet_files"]

    def iterable_rows(
        self, offset: int = 0, limit: str | None = None, **kwargs
    ) -> Iterable[dict]:
        """Iterate over the rows of the dataset"""
        current_page = self.rows(offset=offset, **kwargs)["rows"]

        count = 0
        while current_page:
            for row in current_page:
                if limit == count:
                    return
                yield row
                count += 1

            offset += len(current_page)
            current_page = self.rows(offset=offset, **kwargs)["rows"]

    def iterable_search(
        self, query: str, offset: int = 0, limit: str | None = None, **kwargs
    ) -> Iterable[dict]:
        """Iterate over the rows of the dataset applying a full text search"""
        current_page = self.search(query=query, offset=offset, **kwargs)["rows"]

        count = 0
        while current_page:
            for row in current_page:
                if limit == count:
                    return
                yield row
                count += 1

            offset += len(current_page)
            current_page = self.search(query=query, offset=offset, **kwargs)["rows"]

    def iterable_filter(
        self, where: str, offset: int = 0, limit: str | None = None, **kwargs
    ) -> Iterable[dict]:
        """Iterate over the rows of the dataset applying a filter"""
        current_page = self.filter(where=where, offset=offset, **kwargs)["rows"]

        count = 0
        while current_page:
            for row in current_page:
                if limit == count:
                    return
                yield row
                count += 1

            offset += len(current_page)
            current_page = self.filter(where=where, offset=offset, **kwargs)["rows"]

    @classmethod
    def _raise_for_status(cls, response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as ex:
            cls._LOGGER.error(f"Server error: {ex.response.json()}")
            raise ex

    def _resolve_config(self) -> str:
        splits = self.splits()

        configs = set([split["config"] for split in splits])

        if len(configs) > 1:
            warnings.warn(f"Multiple configs found: {configs}. Using the first one.")

        return next(iter(configs))

    def _resolve_split(self) -> str:
        splits = self.splits()

        splits = set([split["split"] for split in splits])

        if len(splits) > 1:
            warnings.warn(f"Multiple splits found: {splits}. Using the first one.")

        return next(iter(splits))

    def _page_offset_for_row_id(self, row_idx: int) -> int:
        return self._batch_size * (row_idx // self._batch_size)
