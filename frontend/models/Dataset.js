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

import { Model } from "@vuex-orm/core";

import DatasetViewSettings from "./DatasetViewSettings";

const USER_DATA_METADATA_KEY = "rubrix.recogn.ai/ui/custom/userData.v1";

class ObservationDataset extends Model {
  static entity = "datasets";

  // TODO: Combine name + owner for primary key.
  //  This should fix https://github.com/recognai/rubrix/issues/736
  static primaryKey = ["owner", "name"];

  static #registeredDatasetClasses = {};

  static registerTaskDataset(task, datasetClass) {
    this.#registeredDatasetClasses[task] = datasetClass;
  }

  static getClassDatasetForTask(taskName) {
    return this.#registeredDatasetClasses[taskName];
  }

  getTaskDatasetClass() {
    return ObservationDataset.getClassDatasetForTask(this.task);
  }
  async initialize() {}

  async fetchMetricSummary(metricId) {
    try {
      const { response } = await ObservationDataset.api().post(
        `/datasets/${this.task}/${this.name}/metrics/${metricId}:summary`,
        {},
        {
          save: false,
        }
      );
      return response.data;
    } catch (error) {
      return { labels: [] };
    }
  }

  get id() {
    return [this.owner, this.name];
  }

  get visibleRecords() {
    return this.results.records.slice(0, this.viewSettings.pagination.size);
  }

  static fields() {
    return {
      name: this.string(null),
      owner: this.string(null),
      metadata: this.attr(null),
      tags: this.attr(null),
      task: this.string(null),
      created_at: this.string(null),
      last_updated: this.string(null),
      // This will be normalized in a future PR using also owner for relational ids
      viewSettings: this.hasOne(DatasetViewSettings, "id", "name"),
    };
  }
}

export { ObservationDataset, USER_DATA_METADATA_KEY };
