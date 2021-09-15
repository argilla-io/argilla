import { Text2TextDataset } from "@/models/Text2Text";

const getters = {};

const actions = {
  async updateRecords(_, { dataset, records }) {
    return await Text2TextDataset.api().post(
      `/datasets/${dataset.name}/Text2Text:bulk`,
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
          sentences: values,
        },
      };
    });

    return await dispatch("updateRecords", { dataset, records: newRecords });
  },

  async search(store, { dataset, query, sort, size }) {
    query = query || {};
    sort = sort || [];
    const save = size == 0 ? false : true;

    const results = await Text2TextDataset.api().post(
      `/datasets/${dataset.name}/Text2Text:search?limit=0`
    );
    let globalResultsData = results.response.data;

    return await Text2TextDataset.api().post(
      `/datasets/${dataset.name}/Text2Text:search?limit=${size}`,
      {
        query: { ...query, query_text: query.text },
        sort,
      },
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
    return await Text2TextDataset.api().post(
      `/datasets/${dataset.name}/Text2Text:search?limit=${size}&from=${from}`,
      {
        query: { ...dataset.query, query_text: dataset.query.text },
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
