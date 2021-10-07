/*
 * coding=utf-8
 * Copyright 2021-present, the Recognai S.L. team.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { ObservationDataset, USER_DATA_METADATA_KEY } from "./Dataset";
import { BaseRecord, BaseSearchQuery, BaseSearchResults } from "./Common";

class TextClassificationRecord extends BaseRecord {
  inputs;

  constructor({
    inputs,
    explanation,
    multi_label,
    predicted_as,
    ...superData
  }) {
    super(superData);
    this.inputs = inputs;
    this.explanation = explanation;
    this.multi_label = multi_label;
    this.predicted_as = predicted_as;
  }

  recordTitle() {
    return this.inputs;
  }
}

class TextClassificationSearchQuery extends BaseSearchQuery {
  score;

  constructor(data) {
    const { score, confidence, ...superData } = data;
    super(superData);
    this.score = score;
    // TODO: remove backward compatibility
    if (confidence) {
      this.score = confidence;
    }
  }
}

class TextClassificationSearchResults extends BaseSearchResults {
  constructor({ total, records, aggregations }) {
    super({
      total,
      aggregations,
      records: (records || []).map(
        (record) => new TextClassificationRecord(record)
      ),
    });
  }
}

class TextClassificationDataset extends ObservationDataset {
  static entity = "text_classification";

  static fields() {
    return {
      ...super.fields(),
      query: this.attr({}, (data) => {
        return new TextClassificationSearchQuery(data);
      }),
      sort: this.attr([]),
      results: this.attr(
        {},
        (data) => new TextClassificationSearchResults(data)
      ),
      globalResults: this.attr({}),
    };
  }

  get labels() {
    const { labels } = (this.metadata || {})[USER_DATA_METADATA_KEY] || {};
    const aggregations = this.globalResults.aggregations;

    const uniqueLabels = [
      ...new Set(
        (labels || [])
          .filter((l) => l && l.trim())
          .concat(Object.keys(aggregations.annotated_as))
          .concat(Object.keys(aggregations.predicted_as))
      ),
    ];
    uniqueLabels.sort();
    return uniqueLabels;
  }
}

ObservationDataset.registerTaskDataset(
  "TextClassification",
  TextClassificationDataset
);

export {
  TextClassificationDataset,
  TextClassificationRecord,
  TextClassificationSearchResults,
  TextClassificationSearchQuery,
};
