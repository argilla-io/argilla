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

AVAILABLE_SIZE_CATEGORIES = {
    1_000: "n<1K",
    10_000: "1K<n<10K",
    100_000: "10K<n<100K",
    1_000_000: "100K<n<1M",
    10_000_000: "1M<n<10M",
    100_000_000: "10M<n<100M",
    1_000_000_000: "100M<n<1B",
    10_000_000_000: "1B<n<10B",
    100_000_000_000: "10B<n<100B",
    1_000_000_000_000: "100B<n<1T",
}


def size_categories_parser(input_size: int) -> str:
    for size, category in AVAILABLE_SIZE_CATEGORIES.items():
        if input_size < size:
            return category
    return "n>1T"
