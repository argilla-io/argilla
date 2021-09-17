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
import { TokenClassificationDataset } from "@/models/TokenClassification";

const getters = {};

const actions = {
  async setEntities(_, { dataset, entities }) {
    return await ObservationDataset.dispatch("setUserData", {
      dataset,
      data: { entities },
    });
  },
  async updateRecords(_, { dataset, records }) {
    return await TokenClassificationDataset.api().post(
      `/datasets/${dataset.name}/TokenClassification:bulk`,
      {
        name: dataset.name,
        records,
      }
    );
  },

  async search(store, { dataset, query, sort, size }) {
    query = query || {};
    sort = sort || [];
    const save = size == 0 ? false : true;

    const results = await TokenClassificationDataset.api().post(
      `/datasets/${dataset.name}/TokenClassification:search?limit=0`
    );
    let globalResultsData = results.response.data;

    return await TokenClassificationDataset.api().post(
      `/datasets/${dataset.name}/TokenClassification:search?limit=${size}`,
      {
        query: { ...query, query_text: query.text },
        sort,
      }, // search body
      {
        save,
        dataTransformer: ({ data }) => {
          return {
            ...dataset,
            results: data,
            globalResults: globalResultsData,
            query,
            sort,
          };
        },
      }
    );
  },

  async paginate(store, { dataset, size, from }) {
    return await TokenClassificationDataset.api().post(
      `/datasets/${dataset.name}/TokenClassification:search?limit=${size}&from=${from}`,
      {
        query: { ...dataset.query, query_text: dataset.query.text },
        sort: dataset.sort,
      },
      {
        dataTransformer: ({ data }) => {
          return {
            ...dataset.$toJson(),
            results: {
              ...dataset.results,
              records: data.records,
            },
          };
        },
      }
    );
  },
};

export default {
  getters,
  actions,
};
