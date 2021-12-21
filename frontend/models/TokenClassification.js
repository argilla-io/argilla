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

class TokenClassificationRecord extends BaseRecord {
  tokens;
  raw_text;

  visualTokens;

  constructor({ tokens, raw_text, ...superData }) {
    super({ ...superData });
    const { visualTokens } = tokens.reduce(
      ({ visualTokens, startPosition }, token) => {
        const start = raw_text.indexOf(token, startPosition);
        const end = start + token.length;
        return {
          visualTokens: [...visualTokens, { start, end, text: token }],
          startPosition: end,
        };
      },
      {
        visualTokens: [],
        startPosition: 0,
      }
    );
    this.tokens = tokens;
    this.raw_text = raw_text;
    this.visualTokens = visualTokens;
  }

  recordTitle() {
    return this.raw_text;
  }
}

class TokenClassificationSearchQuery extends BaseSearchQuery {
  query_text;

  constructor({ query_text, ...superData }) {
    super(superData);
    this.query_text = query_text;
  }
}

class TokenClassificationSearchResults extends BaseSearchResults {
  constructor({ total, records, aggregations }) {
    super({
      total,
      aggregations,
      records: (records || []).map(
        (record) => new TokenClassificationRecord(record)
      ),
    });
  }
}

class TokenClassificationDataset extends ObservationDataset {
  static entity = "token_classification";

  static fields() {
    return {
      ...super.fields(),
      query: this.attr({}, (data) => {
        return new TokenClassificationSearchQuery(data);
      }),
      sort: this.attr([]),
      results: this.attr(
        {},
        (data) => new TokenClassificationSearchResults(data)
      ),
      globalResults: this.attr({}),
    };
  }

  get entities() {
    const { entities } = (this.metadata || {})[USER_DATA_METADATA_KEY] || {};
    const aggregations = this.globalResults.aggregations;
    const names = [
      ...new Set(
        (entities || [])
          .filter((e) => e && e.trim())
          .concat(Object.keys(aggregations.annotated_as))
          .concat(Object.keys(aggregations.predicted_as))
      ),
    ];
    return names.map((name, index) => {
      return {
        colorId: index,
        text: name,
      };
    });
  }
}

ObservationDataset.registerTaskDataset(
  "TokenClassification",
  TokenClassificationDataset
);

export {
  TokenClassificationDataset,
  TokenClassificationRecord,
  TokenClassificationSearchResults,
  TokenClassificationSearchQuery,
};
