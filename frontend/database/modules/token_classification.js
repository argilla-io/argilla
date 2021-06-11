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

  async fetchMoreRecords(store, { dataset, size, from }) {
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
