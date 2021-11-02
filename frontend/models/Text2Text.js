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

import { ObservationDataset } from "./Dataset";
import { BaseRecord, BaseSearchQuery, BaseSearchResults } from "./Common";

class Text2TextRecord extends BaseRecord {
  text;

  constructor({ text, ...superData }) {
    super(superData);
    this.text = text;
  }
  recordTitle() {
    return this.text;
  }
}

class Text2TextSearchQuery extends BaseSearchQuery {
  score;

  constructor(data) {
    const { score, ...superData } = data;
    super(superData);

    this.score = score;
  }
}

class Text2TextSearchResults extends BaseSearchResults {
  constructor({ total, records, aggregations }) {
    super({
      total,
      aggregations,
      records: (records || []).map((record) => new Text2TextRecord(record)),
    });
  }
}

class Text2TextDataset extends ObservationDataset {
  static entity = "text2_text";

  static fields() {
    return {
      ...super.fields(),
      query: this.attr({}, (data) => {
        return new Text2TextSearchQuery(data);
      }),
      sort: this.attr([]),
      results: this.attr({}, (data) => new Text2TextSearchResults(data)),
      globalResults: this.attr({}),
    };
  }
}

ObservationDataset.registerTaskDataset("Text2Text", Text2TextDataset);

export {
  Text2TextDataset,
  Text2TextRecord,
  Text2TextSearchResults,
  Text2TextSearchQuery,
};
