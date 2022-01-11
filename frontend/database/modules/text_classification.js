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

import { ObservationDataset } from "@/models/Dataset";

const getters = {};

const actions = {
  async setLabels(_, { dataset, labels }) {
    return await ObservationDataset.dispatch("setUserData", {
      dataset,
      data: { labels },
    });
  },
  async getRules(_, { dataset }) {
    const { response } = await ObservationDataset.api().get(
      `/datasets/${dataset.task}/${dataset.name}/labeling/rules`
    );
    return response.data;
  },

  async defineRule(_, { dataset, label }) {
    await ObservationDataset.api().post(
      `/datasets/${dataset.task}/${dataset.name}/labeling/rules`,
      {
        query: dataset.query.text,
        label: label,
        description: dataset.query.text,
      }
    );
  },

  async updateRule(_, { dataset, label }) {
    await ObservationDataset.api().patch(
      `/datasets/${dataset.task}/${dataset.name}/labeling/rules/${dataset.query.text}`,
      {
        label: label,
        description: dataset.query.text,
      }
    );
  },

  async getRule(_, { dataset, query }) {
    const { response } = await ObservationDataset.api().get(
      `/datasets/${dataset.task}/${dataset.name}/labeling/rules/${query}`,
      {
        // Ignore errors related to rule not found
        validateStatus: function (status) {
          return status === 404 || (status >= 200 && status < 300);
        },
      }
    );
    if (response.status === 404) {
      return undefined;
    }
    return response.data;
  },

  async deleteRule(_, { dataset, query }) {
    await ObservationDataset.api().delete(
      `/datasets/${dataset.task}/${dataset.name}/labeling/rules/${query}`
    );
  },

  async getRulesMetrics(_, { dataset }) {
    const { response } = await ObservationDataset.api().get(
      `/datasets/${dataset.task}/${dataset.name}/labeling/rules/metrics`
    );
    return response.data;
  },

  async getRuleMetricsByLabel(_, { dataset, query, label }) {
    var url = `/datasets/${dataset.task}/${dataset.name}/labeling/rules/${query}/metrics`;
    if (label !== undefined) {
      url += `?label=${label}`;
    }
    const { response } = await ObservationDataset.api().get(url);
    return response.data;
  },
};

export default {
  getters,
  actions,
};
