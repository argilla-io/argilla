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

import {
  ObservationDataset,
  USER_DATA_METADATA_KEY,
  getDatasetModelPrimaryKey,
} from "./Dataset";
import { BaseRecord, BaseSearchQuery, BaseSearchResults } from "./Common";
import { TokenEntity } from "./token-classification/TokenEntity.modelTokenClassification";
import { TokenRecord } from "./token-classification/TokenRecord.modelTokenClassification";

class TokenClassificationRecord extends BaseRecord {
  // tokens;
  // text;
  constructor({ tokens, text, annotatedEntities, ...superData }) {
    super({ ...superData });
    this.tokens = tokens;
    this.text = text;

    if (!annotatedEntities) {
      if (this.annotation) {
        annotatedEntities = this.annotation.entities.map((obj) => ({
          ...obj,
          origin: "annotation",
        }));
      } else if (this.prediction) {
        annotatedEntities = this.prediction.entities.map((obj) => ({
          ...obj,
          origin: "prediction",
        }));
      } else {
        annotatedEntities = [];
      }
    }

    this.annotatedEntities = annotatedEntities;
  }

  recordTitle() {
    return this.text;
  }

  get clipboardText() {
    return this.text;
  }
}

class TokenClassificationSearchQuery extends BaseSearchQuery {
  score;
  query_text;

  constructor({ score, query_text, ...superData }) {
    super(superData);
    this.score = score;
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
      settings: this.attr({}),
      query: this.attr({}, (data) => {
        return new TokenClassificationSearchQuery(data);
      }),
      sort: this.attr([]),
      results: this.attr(
        {},
        (data) => new TokenClassificationSearchResults(data)
      ),
      globalResults: this.attr({}),
      lastSelectedEntity: this.attr({}),

      //relationships
      token_entities: this.hasMany(TokenEntity, "dataset_id"),
      token_records: this.hasMany(TokenRecord, "dataset_id"),
    };
  }

  async initialize() {
    const settings = await this._getDatasetSettings();
    const entity = this.getTaskDatasetClass();
    await entity.insertOrUpdate({
      where: this.id,
      data: [
        {
          owner: this.owner,
          name: this.name,
          settings,
        },
      ],
    });

    return entity.find(getDatasetModelPrimaryKey(this));
  }

  get entities() {
    const formatEntities = (entities = []) =>
      entities.map((name, index) => {
        return {
          colorId: index,
          text: name,
        };
      });
    const predefinedEntities =
      this.settings.label_schema && this.settings.label_schema.labels;

    if (predefinedEntities) {
      return formatEntities(predefinedEntities.map((l) => l.id));
    }
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

    return formatEntities(names);
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
