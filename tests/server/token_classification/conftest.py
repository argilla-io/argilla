#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pytest

from argilla.server.apis.v0.models.token_classification import TokenClassificationRecord


@pytest.fixture(scope="session")
def records_for_token_classification():

    return [
        {
            "id": "0003fdaf-344d-4d91-a9aa-87b5203c501e",
            "metadata": {},
            "status": "Validated",
            "annotation": {
                "agent": "MacBook-Pro-de-Francisco.local",
                "entities": [{"start": 0, "end": 6, "label": "ORG", "score": 1.0}],
            },
            "annotations": {
                "MacBook-Pro-de-Francisco.local": {
                    "entities": [{"start": 0, "end": 6, "label": "ORG", "score": 1.0}]
                }
            },
            "metrics": {},
            "last_updated": "2022-10-14T13:23:13.105981",
            "text": "Oxford 4 1 0 3 6 5 3",
            "tokens": ["Oxford", "4", "1", "0", "3", "6", "5", "3"],
        },
        {
            "id": "0014b5e9-1c72-43b3-9394-af60bb05588c",
            "metadata": {},
            "status": "Validated",
            "annotation": {
                "agent": "MacBook-Pro-de-Francisco.local",
                "entities": [{"start": 0, "end": 6, "label": "ORG", "score": 1.0}],
            },
            "annotations": {
                "MacBook-Pro-de-Francisco.local": {
                    "entities": [{"start": 0, "end": 6, "label": "ORG", "score": 1.0}]
                }
            },
            "metrics": {},
            "last_updated": "2022-10-14T13:22:49.218421",
            "text": "Pohang 2 1 1 11 10 7",
            "tokens": ["Pohang", "2", "1", "1", "11", "10", "7"],
        },
        {
            "id": "001c7ff5-dcd5-4142-9f32-762aa3de0993",
            "metadata": {},
            "status": "Validated",
            "annotation": {
                "agent": "MacBook-Pro-de-Francisco.local",
                "entities": [
                    {"start": 78, "end": 85, "label": "LOC", "score": 1.0},
                    {"start": 98, "end": 112, "label": "MISC", "score": 1.0},
                    {"start": 143, "end": 153, "label": "LOC", "score": 1.0},
                ],
            },
            "annotations": {
                "MacBook-Pro-de-Francisco.local": {
                    "entities": [
                        {"start": 78, "end": 85, "label": "LOC", "score": 1.0},
                        {"start": 98, "end": 112, "label": "MISC", "score": 1.0},
                        {"start": 143, "end": 153, "label": "LOC", "score": 1.0},
                    ]
                }
            },
            "metrics": {},
            "last_updated": "2022-10-14T13:24:41.139767",
            "text": "Her official programme will begin on Monday , and she will leave that day for Bolivia to attend a Latin American summit meeting in the city of Cochabamba .",
            "tokens": [
                "Her",
                "official",
                "programme",
                "will",
                "begin",
                "on",
                "Monday",
                ",",
                "and",
                "she",
                "will",
                "leave",
                "that",
                "day",
                "for",
                "Bolivia",
                "to",
                "attend",
                "a",
                "Latin",
                "American",
                "summit",
                "meeting",
                "in",
                "the",
                "city",
                "of",
                "Cochabamba",
                ".",
            ],
        },
        {
            "id": "001fde14-5735-49a6-a8ff-0bb48edfd337",
            "metadata": {},
            "status": "Validated",
            "annotation": {
                "agent": "MacBook-Pro-de-Francisco.local",
                "entities": [{"start": 11, "end": 23, "label": "MISC", "score": 1.0}],
            },
            "annotations": {
                "MacBook-Pro-de-Francisco.local": {
                    "entities": [
                        {"start": 11, "end": 23, "label": "MISC", "score": 1.0}
                    ]
                }
            },
            "metrics": {},
            "last_updated": "2022-10-14T13:24:07.514590",
            "text": "BASEBALL - MAJOR LEAGUE STANDINGS AFTER THURSDAY 'S GAMES .",
            "tokens": [
                "BASEBALL",
                "-",
                "MAJOR",
                "LEAGUE",
                "STANDINGS",
                "AFTER",
                "THURSDAY",
                "'S",
                "GAMES",
                ".",
            ],
        },
        {
            "id": "00315ed3-a2d6-43b0-8f52-93404f7c10b7",
            "metadata": {},
            "status": "Validated",
            "annotation": {
                "agent": "MacBook-Pro-de-Francisco.local",
                "entities": [
                    {"start": 3, "end": 11, "label": "PER", "score": 1.0},
                    {"start": 17, "end": 21, "label": "LOC", "score": 1.0},
                    {"start": 26, "end": 46, "label": "ORG", "score": 1.0},
                ],
            },
            "annotations": {
                "MacBook-Pro-de-Francisco.local": {
                    "entities": [
                        {"start": 3, "end": 11, "label": "PER", "score": 1.0},
                        {"start": 17, "end": 21, "label": "LOC", "score": 1.0},
                        {"start": 26, "end": 46, "label": "ORG", "score": 1.0},
                    ]
                }
            },
            "metrics": {},
            "last_updated": "2022-10-14T13:24:37.882821",
            "text": "7. Al Unser Jr ( U.S. ) , Penske Mercedes-Benz , 54.683",
            "tokens": [
                "7.",
                "Al",
                "Unser",
                "Jr",
                "(",
                "U.S.",
                ")",
                ",",
                "Penske",
                "Mercedes-Benz",
                ",",
                "54.683",
            ],
        },
        {
            "id": "004559c6-89f1-4f44-9922-111201381ede",
            "metadata": {},
            "status": "Validated",
            "annotation": {
                "agent": "MacBook-Pro-de-Francisco.local",
                "entities": [
                    {"start": 0, "end": 8, "label": "MISC", "score": 1.0},
                    {"start": 67, "end": 71, "label": "LOC", "score": 1.0},
                    {"start": 98, "end": 102, "label": "LOC", "score": 1.0},
                    {"start": 121, "end": 129, "label": "MISC", "score": 1.0},
                ],
            },
            "annotations": {
                "MacBook-Pro-de-Francisco.local": {
                    "entities": [
                        {"start": 0, "end": 8, "label": "MISC", "score": 1.0},
                        {"start": 67, "end": 71, "label": "LOC", "score": 1.0},
                        {"start": 98, "end": 102, "label": "LOC", "score": 1.0},
                        {"start": 121, "end": 129, "label": "MISC", "score": 1.0},
                    ]
                }
            },
            "metrics": {},
            "last_updated": "2022-10-14T13:24:27.384141",
            "text": "Canadian bonds opened softer on Friday , pulled lower by a sinking U.S. market , but outperformed U.S. bonds on positive Canadian economic data , analysts said .",
            "tokens": [
                "Canadian",
                "bonds",
                "opened",
                "softer",
                "on",
                "Friday",
                ",",
                "pulled",
                "lower",
                "by",
                "a",
                "sinking",
                "U.S.",
                "market",
                ",",
                "but",
                "outperformed",
                "U.S.",
                "bonds",
                "on",
                "positive",
                "Canadian",
                "economic",
                "data",
                ",",
                "analysts",
                "said",
                ".",
            ],
        },
    ]
