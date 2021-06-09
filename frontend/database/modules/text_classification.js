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
            confidence: 1.0,
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

    const results = await TextClassificationDataset.api().post(`/datasets/${dataset.name}/TextClassification:search?limit=0`)
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
          return { ...dataset, results: data, globalResults: globalResultsData, query, sort};
        },
      }
    );
  },

  async fetchMoreRecords(store, { dataset, size, from }) {
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
              records: dataset.results.records.concat(data.records),
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
