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
import { TextClassificationDataset } from "@/models/TextClassification";

const getters = {};

const actions = {
  async setLabels(_, { dataset, labels }) {
    return await ObservationDataset.dispatch("setUserData", {
      dataset,
      data: { labels },
    });
  },
  async updateRecords(_, { dataset, records }) {
    return await TextClassificationDataset.api().post(
      `/datasets/${dataset.name}/TextClassification:bulk`,
      {
        name: dataset.name,
        records,
      }
    );
  },
  async discardAnnotations({ dispatch }, { dataset, records }) {
    const newRecords = records.map((record) => ({
      ...record,
      status: "Discarded",
    }));
    return await dispatch("updateRecords", { dataset, records: newRecords });
  },

  async validateAnnotations({ dispatch }, { dataset, records }) {
    const newRecords = records.map((record) => ({
      ...record,
      status: "Validated",
    }));
    return await dispatch("updateRecords", { dataset, records: newRecords });
  },

  async annotate({ dispatch }, { dataset, records, values, annotatedBy }) {
    const newRecords = records.map((record) => {
      return {
        ...record,
        status: "Validated",
        annotation: {
          agent: annotatedBy,
          labels: values.map((label) => ({
            class: label,
            score: 1.0,
          })),
        },
      };
    });

    return await dispatch("updateRecords", { dataset, records: newRecords });
  },

  async search(store, { dataset, query, sort, size }) {
    query = query || {};
    sort = sort || [];
    const save = size == 0 ? false : true;

    const results = await TextClassificationDataset.api().post(
      `/datasets/${dataset.name}/TextClassification:search?limit=0`
    );
    let globalResultsData = results.response.data;

    return await TextClassificationDataset.api().post(
      `/datasets/${dataset.name}/TextClassification:search?limit=${size}`,
      {
        query: { ...query, query_inputs: query.text },
        sort,
      },
      {
        save,
        dataTransformer: ({ data }) => {
          return {
            ...dataset,
            results: {
              ...data,
              aggregations: {
                score: (data.aggregations || {}).confidence,
                ...data.aggregations,
              },
              records: data.records.map(
                // TODO: remove backward
                ({ prediction, annotation, ...record }) => {
                  if (prediction) {
                    prediction.labels = prediction.labels.map(
                      ({ confidence, ...label }) => ({
                        score: confidence,
                        ...label,
                      })
                    );
                  }
                  if (annotation) {
                    annotation.labels = annotation.labels.map(
                      ({ confidence, ...label }) => ({
                        score: confidence,
                        ...label,
                      })
                    );
                  }
                  return { ...record, prediction, annotation };
                }
              ),
            },
            globalResults: globalResultsData,
            query,
            sort,
          };
        },
      }
    );
  },

  async paginate(store, { dataset, size, from }) {
    return await TextClassificationDataset.api().post(
      `/datasets/${dataset.name}/TextClassification:search?limit=${size}&from=${from}`,
      {
        query: { ...dataset.query, query_inputs: dataset.query.text },
        sort: dataset.sort,
      },
      {
        dataTransformer: ({ data }) => {
          return {
            ...dataset,
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
