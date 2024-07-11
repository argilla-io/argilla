# Copyright 2024-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from argilla import (
    Argilla,
    Settings,
    TextField,
    TextQuestion,
    SpanQuestion,
    LabelQuestion,
    MultiLabelQuestion,
    RatingQuestion,
    RankingQuestion,
    TermsMetadataProperty,
    IntegerMetadataProperty,
    FloatMetadataProperty,
)


def test_publish_dataset(client: "Argilla"):
    new_ws = client.workspaces("new_ws")
    if not new_ws.exists():
        new_ws.create()

    assert new_ws.exists(), "The workspace was not created"

    ds = client.datasets("new_ds", workspace=new_ws)
    if ds.exists():
        ds.delete()

    assert not ds.exists(), "The dataset was not deleted"

    ds.settings = Settings(
        guidelines="This is a test dataset",
        allow_extra_metadata=True,
        fields=[TextField(name="text-field")],
        questions=[
            TextQuestion(name="text-question"),
            RatingQuestion(name="rating-question", values=[1, 2, 3, 4, 5]),
            RankingQuestion(name="ranking-question", values=["rank1", "rank2", "rank3"]),
            LabelQuestion(name="label-question", labels=["A", "B", "C"]),
            MultiLabelQuestion(name="multi-label-question", labels=["A", "B", "C"]),
            SpanQuestion(name="span-question", field="text-field", labels=["label1", "label2"]),
        ],
        metadata=[
            TermsMetadataProperty(name="metadata-property", options=["term1", "term2"]),
            TermsMetadataProperty(name="term-property"),
            IntegerMetadataProperty(name="metadata-property-2", min=0, max=10),
            FloatMetadataProperty(name="metadata-property-3", min=0, max=10),
        ],
    )

    ds.create()

    created_dataset = client.datasets(name=ds.name, workspace=new_ws)
    assert created_dataset.exists(), "The dataset was not found"
    assert created_dataset == ds
    assert created_dataset.settings == ds.settings, "The settings were not saved"

    assert created_dataset.guidelines == ds.guidelines
    assert created_dataset.allow_extra_metadata == ds.allow_extra_metadata
    assert created_dataset.fields == ds.fields
    assert created_dataset.questions == ds.questions
    assert created_dataset.schema == ds.schema
