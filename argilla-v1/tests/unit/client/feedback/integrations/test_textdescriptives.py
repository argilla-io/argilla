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

from unittest.mock import MagicMock

import pandas as pd
import pytest
from argilla_v1.client.feedback.dataset import FeedbackDataset
from argilla_v1.client.feedback.integrations.textdescriptives import TextDescriptivesExtractor
from argilla_v1.client.feedback.schemas.fields import TextField
from argilla_v1.client.feedback.schemas.metadata import (
    FloatMetadataProperty,
    IntegerMetadataProperty,
    TermsMetadataProperty,
)
from argilla_v1.client.feedback.schemas.questions import TextQuestion
from argilla_v1.client.feedback.schemas.records import FeedbackRecord


@pytest.fixture
def records():
    return


@pytest.fixture(scope="session")
def td_extractor() -> TextDescriptivesExtractor:
    return TextDescriptivesExtractor()


@pytest.mark.fixtures("td_extractor")
@pytest.mark.parametrize(
    "records",
    [
        [
            FeedbackRecord(
                fields={"required-field": "This is a test.", "optional-field": None},
            ),
            FeedbackRecord(
                fields={"required-field": "This is another test.", "optional-field": None},
            ),
        ],
        [
            FeedbackRecord(
                fields={"required-field": "This is a test.", "optional-field": "This is also a test."},
            ),
            FeedbackRecord(
                fields={"required-field": "This is another test.", "optional-field": "This is also another test."},
            ),
        ],
        [
            FeedbackRecord(
                fields={"required-field": "This is a test."},
                metadata={"text_n_tokens": 5, "text_n_unique_tokens": 4},
            ),
            FeedbackRecord(
                fields={"required-field": "This is another test."},
                metadata={"text_n_tokens": 5, "text_n_unique_tokens": 4},
            ),
        ],
    ],
)
def test_extract_metrics_for_single_field(records, td_extractor: TextDescriptivesExtractor) -> None:
    field_metrics = td_extractor._extract_metrics_for_single_field(records, "required-field")
    assert field_metrics["required-field_n_tokens"].values[0] == 4
    assert len(field_metrics) == len(records)  # Assert the number of rows in the DataFrame
    assert isinstance(field_metrics, pd.DataFrame)  # Assert the data type of the DataFrame
    assert "required-field_n_tokens" in field_metrics.columns  # Assert the presence of the column
    assert field_metrics["required-field_n_tokens"].values[0] == 4  # Assert the value of the column
    assert "required-field" not in field_metrics.columns  # Assert that text column has been dropped
    assert not field_metrics.isnull().values.any()  # Assert no columns with NaN values
    assert "optional-field" not in field_metrics.columns


@pytest.mark.fixtures("td_extractor")
def test_extract_metrics_for_single_field_empty_field(td_extractor: TextDescriptivesExtractor) -> None:
    records = [
        FeedbackRecord(
            fields={"required-field": "This is a test.", "optional-field": None},
        ),
        FeedbackRecord(
            fields={"required-field": "This is another test.", "optional-field": None},
        ),
    ]
    field_metrics = td_extractor._extract_metrics_for_single_field(records, "optional-field")
    assert field_metrics is None


@pytest.mark.fixtures("td_extractor")
@pytest.mark.parametrize(
    "records",
    [
        [
            FeedbackRecord(
                fields={"required-field": "This is a test.", "optional-field": None},
            ),
            FeedbackRecord(
                fields={"required-field": "This is another test.", "optional-field": None},
            ),
        ],
        [
            FeedbackRecord(
                fields={"required-field": "This is a test.", "optional-field": "This is also a test."},
            ),
            FeedbackRecord(
                fields={"required-field": "This is another test.", "optional-field": "This is also another test."},
            ),
        ],
        [
            FeedbackRecord(
                fields={"required-field": "This is a test."},
                metadata={"text_n_tokens": 5, "text_n_unique_tokens": 4},
            ),
            FeedbackRecord(
                fields={"required-field": "This is another test."},
                metadata={"text_n_tokens": 5, "text_n_unique_tokens": 4},
            ),
        ],
    ],
)
def test_extract_metrics_for_all_fields(records, td_extractor: TextDescriptivesExtractor) -> None:
    expected_fields = [key for record in records for key, value in record.fields.items() if value is not None]
    field_metrics = td_extractor._extract_metrics_for_all_fields(records, overwrite=False, fields=expected_fields)
    assert field_metrics["required-field_n_tokens"].values[0] == 4
    assert all(any(field == col or field + "_" in col for col in field_metrics.columns) for field in expected_fields)


@pytest.mark.fixtures("td_extractor")
def test_cast_to_python_types(td_extractor: TextDescriptivesExtractor) -> None:
    df = pd.DataFrame(
        {
            "col_int": [1, 2, 3],
            "col_bool": [True, False, True],
            "col_float": [1.234, 2.345, 3.456],
        }
    )
    df_result = td_extractor._cast_to_python_types(df)
    assert df_result["col_int"].dtype == "int32" or df_result["col_int"].dtype == "int64"
    assert df_result["col_bool"].dtype == "object"
    assert df_result["col_float"].dtype == "float64" or df_result["col_float"].dtype == "float32"
    assert df_result["col_float"].values[0] == 1.23
    assert isinstance(df_result, pd.DataFrame)


@pytest.mark.fixtures("td_extractor")
def test_clean_column_name(td_extractor: TextDescriptivesExtractor) -> None:
    assert td_extractor._clean_column_name("Test_Col") == "test_col"
    assert td_extractor._clean_column_name("test col") == "test_col"
    assert td_extractor._clean_column_name("Test-Col") == "test_col"
    assert td_extractor._clean_column_name("Test.Col") == "test_col"


@pytest.mark.fixtures("td_extractor")
@pytest.mark.parametrize(
    "column_name, expected_prop_type, expected_title, expected_visible, expected_type, expected_values",
    [
        ("col_int", IntegerMetadataProperty, "Col Int", True, "integer", None),
        ("col_bool", TermsMetadataProperty, "Col Bool", True, "terms", ["True", "False"]),
        ("col_float", FloatMetadataProperty, "Col Float", True, "float", None),
        ("col_obj", TermsMetadataProperty, "Col Obj", True, "terms", ["value_1", "value_2", "value_3"]),
    ],
)
def test_create_metadata_properties(
    column_name,
    expected_prop_type,
    expected_title,
    expected_visible,
    expected_type,
    expected_values,
    td_extractor: TextDescriptivesExtractor,
) -> None:
    df = pd.DataFrame(
        {
            "col_int": pd.Series([1, 2, 3], dtype="int32"),
            "col_bool": pd.Series([True, False, True], dtype="bool"),
            "col_float": pd.Series([1.234, 2.345, 3.456], dtype="float64"),
            "col_obj": pd.Series(["value_1", "value_2", "value_3"], dtype="object"),
        }
    )
    properties = td_extractor._create_metadata_properties(df)
    prop = next((prop for prop in properties if prop.name == column_name), None)
    assert isinstance(prop, expected_prop_type)
    assert prop.name == column_name
    assert prop.title == expected_title
    assert prop.visible_for_annotators == expected_visible
    assert prop.type == expected_type
    if isinstance(prop, TermsMetadataProperty):
        assert prop.values == expected_values


@pytest.mark.fixtures("td_extractor")
@pytest.mark.parametrize(
    "records",
    [
        [
            FeedbackRecord(
                fields={"required-field": "This is a test.", "optional-field": None},
            ),
            FeedbackRecord(
                fields={"required-field": "This is another test.", "optional-field": None},
            ),
        ],
        [
            FeedbackRecord(
                fields={"required-field": "This is a test.", "optional-field": "This is also a test."},
            ),
            FeedbackRecord(
                fields={"required-field": "This is another test.", "optional-field": "This is also another test."},
            ),
        ],
        [
            FeedbackRecord(
                fields={"required-field": "This is a test."},
                metadata={"text_n_tokens": 5, "text_n_unique_tokens": 4},
            ),
            FeedbackRecord(
                fields={"required-field": "This is another test."},
                metadata={"text_n_tokens": 5, "text_n_unique_tokens": 4},
            ),
        ],
    ],
)
def test_update_records_metrics_extracted(records, td_extractor: TextDescriptivesExtractor) -> None:
    extracted_metrics = pd.DataFrame({"text_n_tokens": [4, 5]})
    td_extractor._extract_metrics_for_all_fields = MagicMock(return_value=extracted_metrics)
    td_extractor._cast_to_python_types = MagicMock(return_value=extracted_metrics)
    td_extractor._clean_column_name = MagicMock(side_effect=lambda col: col)
    td_extractor._add_text_descriptives_to_metadata = MagicMock(return_value=records)
    updated_records = td_extractor.update_records(records)
    td_extractor._extract_metrics_for_all_fields.assert_called_once()
    td_extractor._cast_to_python_types.assert_called_once_with(extracted_metrics)
    td_extractor._clean_column_name.assert_called_with("text_n_tokens")
    td_extractor._add_text_descriptives_to_metadata.assert_called_once_with(records, extracted_metrics)
    assert updated_records == records


@pytest.mark.fixtures("td_extractor")
def test_update_records_no_metrics_extracted(td_extractor: TextDescriptivesExtractor):
    records = [
        FeedbackRecord(fields={"text": "This is a test."}),
        FeedbackRecord(fields={"text": "This is another test."}),
    ]
    td_extractor._extract_metrics_for_all_fields = MagicMock(return_value=pd.DataFrame())
    updated_records = td_extractor.update_records(records)
    assert updated_records == records


@pytest.mark.fixtures("td_extractor")
def test_update_feedback_dataset(td_extractor: TextDescriptivesExtractor):
    dataset = FeedbackDataset(
        fields=[TextField(name="text")],
        questions=[TextQuestion(name="question")],
    )
    records = [
        FeedbackRecord(fields={"text": "This is a test."}),
        FeedbackRecord(fields={"text": "This is another test."}),
    ]
    dataset.add_records(records)

    extracted_metrics = pd.DataFrame({"text_n_tokens": [4, 5]})
    td_extractor._extract_metrics_for_all_fields = MagicMock(return_value=extracted_metrics)
    td_extractor._cast_to_python_types = MagicMock(return_value=extracted_metrics)
    td_extractor._clean_column_name = MagicMock(side_effect=lambda col: col)
    td_extractor._create_metadata_properties = MagicMock(return_value=[IntegerMetadataProperty(name="text_n_tokens")])

    updated_dataset = td_extractor.update_dataset(dataset, update_records=False)

    td_extractor._extract_metrics_for_all_fields.call_count == 1

    updated_dataset = td_extractor.update_dataset(dataset, update_records=True)

    td_extractor._extract_metrics_for_all_fields.call_count == 3
    td_extractor._cast_to_python_types.assert_called_with(extracted_metrics)
    td_extractor._clean_column_name.assert_called_with("text_n_tokens")
    td_extractor._create_metadata_properties.assert_called_with(extracted_metrics)
    assert updated_dataset == dataset
    assert isinstance(updated_dataset, FeedbackDataset)
    assert updated_dataset.metadata_properties == [
        IntegerMetadataProperty(
            name="text_n_tokens", title="text_n_tokens", visible_for_annotators=True, type="integer", min=None, max=None
        )
    ]


@pytest.mark.fixtures("td_extractor")
def test_update_dataset_with_invalid_fields(td_extractor: TextDescriptivesExtractor):
    dataset = FeedbackDataset(
        fields=[TextField(name="text")],
        questions=[TextQuestion(name="question")],
    )
    with pytest.raises(ValueError):
        td_extractor.update_dataset(dataset, fields=["my_fake_field"])
