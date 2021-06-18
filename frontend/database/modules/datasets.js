import { ObservationDataset, USER_DATA_METADATA_KEY } from "@/models/Dataset";
import { DatasetViewSettings, Pagination } from "@/models/DatasetViewSettings";
import { Notification } from "@/models/Notifications";
import { TextClassificationDataset } from "@/models/TextClassification";
import { TokenClassificationDataset } from "@/models/TokenClassification";
import { AnnotationProgress } from "@/models/AnnotationProgress";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function toSnakeCase(e) {
  return e
    .match(/([A-Z])/g)
    .reduce((str, c) => str.replace(new RegExp(c), "_" + c.toLowerCase()), e)
    .substring(e.slice(0, 1).match(/([A-Z])/g) ? 1 : 0);
}

const getters = {
  byName: () => (name) => {
    const ds = ObservationDataset.find(name);
    const { task } = configuredRouteParams();
    if (ds === null) {
      return undefined;
    }
    switch (task || ds.task) {
      case "TextClassification":
        return TextClassificationDataset.query()
          .withAllRecursive()
          .whereId(name)
          .first();
      case "TokenClassification":
        return TokenClassificationDataset.query()
          .withAllRecursive()
          .whereId(name)
          .first();
      default:
        console.warn("WRONG!!!");
    }
    return undefined;
  },

  datasetEntity: () => (ds) => {
    switch (ds.task) {
      case "TextClassification":
        return TextClassificationDataset;
      case "TokenClassification":
        return TokenClassificationDataset;
    }
    return undefined;
  },
};

const DEFAULT_QUERY_SIZE = 60;

function configuredRouteParams() {
  return {
    query: JSON.parse($nuxt.$route.query.query || "{}"),
    sort: JSON.parse($nuxt.$route.query.sort || "[]"),
    task: $nuxt.$route.query.task,
    allowAnnotation: $nuxt.$route.query.allowAnnotation || false,
  };
}

function displayQueryParams({ query, sort, task, enableAnnotation }) {
  $nuxt.$router.push({
    query: {
      query: JSON.stringify(query),
      sort: JSON.stringify(sort),
      task: task,
      allowAnnotation: enableAnnotation,
    },
  });
}

const actions = {
  async editAnnotations({ dispatch }, { dataset, records }) {
    const newRecords = records.map((record) => ({
      ...record,
      selected: false,
      status: "Edited",
    }));
    return await dispatch("updateRecords", {
      dataset,
      records: newRecords,
      persistBackend: true,
    });
  },
  async discardAnnotations({ dispatch }, { dataset, records }) {
    const newRecords = records.map((record) => ({
      ...record,
      selected: false,
      status: "Discarded",
    }));
    await dispatch("updateRecords", {
      dataset,
      records: newRecords,
      persistBackend: true,
    });
  },
  async validateAnnotations({ dispatch }, { dataset, records }) {
    const newRecords = records.map((record) => ({
      ...record,
      selected: false,
      status: "Validated",
    }));
    return await dispatch("updateRecords", {
      dataset,
      records: newRecords,
      persistBackend: true,
    });
  },

  async setUserData(_, { dataset, data }) {
    const metadata = {
      [USER_DATA_METADATA_KEY]: data,
    };
    await ObservationDataset.api().patch(`/datasets/${dataset.name}`, {
      metadata,
    });

    return await dataset.$update({
      where: dataset.name,
      data: {
        ...dataset,
        metadata: {
          ...dataset.metadata,
          ...metadata,
        },
      },
    });
  },

  async deleteDataset(_, { name }) {
    return await ObservationDataset.api().delete(`/datasets/${name}`, {
      delete: name,
    });
  },

  async exportAnnotations(_, { name }) {
    const result = await ObservationDataset.api().post(
      `/datasets/${name}/snapshots`,
      {
        save: false,
      }
    );

    const data = result.response.data;
    if (result.response.status >= 400) {
      return Notification.dispatch("notify", {
        message: data,
        type: "error",
      });
    }

    return Notification.dispatch("notify", {
      message: `The export is finished, <strong>${data.id}</strong> is accessible at:<br\> <strong>${data.uri}</strong>`,
      type: "success",
    });
  },

  async refreshAnnotationProgress({ getters }, { dataset }) {
    await sleep(1000); // TODO: Elasticsearch flush delay (change approach)

    const entity = getters.datasetEntity(dataset);
    const {
      response: {
        data: { total, aggregations },
      },
    } = await entity.dispatch("search", {
      dataset,
      query: {},
      size: 0, // Disable persistence
    });

    return await AnnotationProgress.insertOrUpdate({
      data: {
        id: dataset.name + dataset.task,
        total: total,
        validated: aggregations.status.Validated,
        discarded: aggregations.status.Discarded,
        annotatedAs: aggregations.annotated_as,
      },
    });
  },

  async updateRecords(
    { getters, dispatch },
    { dataset, records, persistBackend = false }
  ) {
    if (records.length === 0) {
      return;
    }
    let aggregations = {};
    const entity = getters.datasetEntity(dataset);
    if (persistBackend) {
      await entity.dispatch("updateRecords", {
        dataset,
        records,
      });
    }

    dispatch("refreshAnnotationProgress", { dataset });

    return await entity.update({
      where: dataset.name,
      data: {
        ...dataset,
        results: {
          ...dataset.results,
          aggregations: {
            ...dataset.results.aggregations,
            ...aggregations,
          },
          records: dataset.results.records.map((record) => {
            const found = records.find((r) => r.id === record.id);
            return found || record;
          }),
        },
      },
    });
  },
  async fetchAll() {
    /**
     * Fetch all observation datasets from backend
     */
    return await ObservationDataset.api().get("/datasets/");
  },
  async fetchByName({ dispatch }, name) {
    /**
     * Fetch a observation dataset by name
     */
    let ds = ObservationDataset.find(name);
    if (ds === null) {
      await ObservationDataset.api().get(`/datasets/${name}`);
    }
    ds = ObservationDataset.find(name);
    const { task, allowAnnotation } = configuredRouteParams();
    DatasetViewSettings.insert({
      data: ObservationDataset.all().map((ds) => ({
        pagination: { id: ds.name },
        id: ds.name,
        annotationEnabled: allowAnnotation === "true" ? true : false,
      })),
    });
    return await dispatch("loadViewByTask", {
      dataset: ds,
      value: task || ds.task,
    });
  },

  async load({ dispatch }, dataset) {
    /**
     * Loads a specific dataset for records observation
     */
    if (dataset.task === null) {
      // TODO: Error handling
      console.warn("wat!?", dataset);
      return undefined;
    }

    const { query, sort } = configuredRouteParams();

    return await dispatch("search", {
      dataset,
      query,
      sort,
    });
  },

  async search({ getters, dispatch }, { dataset, query, sort }) {
    query = query || {};
    sort = sort || [];

    const metadata = { ...(dataset.query || {}).metadata, ...query.metadata };
    Object.keys(metadata).forEach((key) => {
      if (metadata[key].length <= 0) {
        delete metadata[key];
      }
    });

    if (Array.isArray(query.predicted) && query.predicted.length > 0) {
      query.predicted = query.predicted[0];
    }
    const searchQuery =
      Object.keys(query).length === 0
        ? query
        : { ...dataset.query, ...query, metadata };
    const entity = getters.datasetEntity(dataset);
    await entity.dispatch("search", {
      dataset,
      query: searchQuery,
      sort,
      size: DEFAULT_QUERY_SIZE,
    });
    const viewSettings = DatasetViewSettings.query().first();
    displayQueryParams({
      query: searchQuery,
      sort,
      task: dataset.task,
      enableAnnotation: viewSettings.annotationEnabled,
    });
    return await dispatch("resetPagination", { dataset });
  },

  async resetPagination(_, { dataset }) {
    return await Pagination.update({
      where: dataset.name,
      data: {
        page: 1,
      },
    });
  },

  async enableAnnotation(_, { dataset, value }) {
    displayQueryParams({
      query: dataset.query,
      sort: dataset.sort,
      task: dataset.task,
      enableAnnotation: value,
    });
    return await DatasetViewSettings.update({
      where: dataset.name,
      data: {
        annotationEnabled: value,
      },
    });
  },

  async loadViewByTask(_, { dataset, value }) {
    await ObservationDataset.dispatch("load", { ...dataset, task: value });
    return await ObservationDataset.update({
      where: dataset.name,
      data: {
        task: value,
      },
    });
  },

  async fetchMoreRecords({ dispatch }, { dataset }) {
    const loadedRecords = dataset.results.records.length;
    const prefetchPaginationSize =
      dataset.visibleRecords.length + dataset.viewSettings.pagination.size;
    if (
      // Prefetch data before reach the end of pagination
      loadedRecords < dataset.results.total &&
      loadedRecords <= prefetchPaginationSize
    ) {
      dispatch(
        `entities/${toSnakeCase(dataset.task)}/fetchMoreRecords`,
        {
          dataset,
          from: loadedRecords,
          size: 2 * loadedRecords,
        },
        { root: true }
      );
    }
    return await Pagination.update({
      where: dataset.name,
      data: {
        page: dataset.viewSettings.pagination.page + 1,
      },
    });
  },
};

export default {
  getters,
  actions,
};
