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

import { ObservationDataset, USER_DATA_METADATA_KEY } from "@/models/Dataset";
import { DatasetViewSettings, Pagination } from "@/models/DatasetViewSettings";
import { Notification } from "@/models/Notifications";
import { Text2TextDataset } from "@/models/Text2Text";
import { TextClassificationDataset } from "@/models/TextClassification";
import { TokenClassificationDataset } from "@/models/TokenClassification";
import { AnnotationProgress } from "@/models/AnnotationProgress";
import { Base64 } from "js-base64";

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
    if (ds === null) {
      return undefined;
    }
    switch (ds.task) {
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
      case "Text2Text":
        return Text2TextDataset.query()
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
      case "Text2Text":
        return Text2TextDataset;
    }
    return undefined;
  },
};

function configuredRouteParams() {
  const { query, sort, allowAnnotation, pagination } = $nuxt.$route.query;
  return {
    query: JSON.parse(query ? Base64.decode(query) : "{}"),
    sort: JSON.parse(sort ? Base64.decode(sort) : "[]"),
    allowAnnotation: allowAnnotation || false,
    pagination: pagination ? JSON.parse(Base64.decode(pagination)) : {},
  };
}

function displayQueryParams({ query, sort, enableAnnotation, pagination }) {
  $nuxt.$router.push({
    query: {
      query: Base64.encodeURI(JSON.stringify(query)),
      sort: Base64.encodeURI(JSON.stringify(sort)),
      allowAnnotation: enableAnnotation,
      pagination: Base64.encodeURI(JSON.stringify(pagination)),
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
  async validateAnnotations({ dispatch }, { dataset, records, agent }) {
    const newRecords = records.map((record) => ({
      ...record,
      annotation: {
        agent,
        ...record.annotation,
      },
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
      message: `The export is finished, <strong>${data.id}</strong> is accessible at:<br/> <strong>${data.uri}</strong>`,
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
    const { allowAnnotation } = configuredRouteParams();
    await DatasetViewSettings.insert({
      data: ObservationDataset.all().map((ds) => ({
        pagination: { id: ds.name },
        id: ds.name,
        annotationEnabled: allowAnnotation === "true" ? true : false,
      })),
    });
    return await dispatch("loadViewByTask", {
      dataset: ds,
      value: ds.task,
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

  async load({ dispatch }, dataset) {
    /**
     * Loads a specific dataset for records observation
     */
    if (dataset.task === null) {
      // TODO: Error handling
      console.warn("wat!?", dataset);
      return undefined;
    }

    const { query, sort, pagination } = configuredRouteParams();
    const loadedDataset = await dispatch("search", {
      dataset,
      query,
      sort,
      size: pagination.size,
    });

    if (pagination && pagination.page > 1) {
      return await dispatch("paginate", {
        dataset: loadedDataset,
        size: pagination.size,
        page: pagination.page,
      });
    }

    return loadedDataset;
  },

  async search({ getters }, { dataset, query, sort, size }) {
    query = query || {};
    sort = sort || dataset.sort || [];

    const metadata = { ...(dataset.query || {}).metadata, ...query.metadata };
    Object.keys(metadata).forEach((key) => {
      if (metadata[key].length <= 0) {
        delete metadata[key];
      }
    });

    if (Array.isArray(query.predicted) && query.predicted.length > 0) {
      query.predicted = query.predicted[0];
    }

    query =
      Object.keys(query).length === 0
        ? {}
        : { ...dataset.query, ...query, metadata };

    size = size || new Pagination().size;

    const entity = getters.datasetEntity(dataset);
    try {
      DatasetViewSettings.update({
        where: dataset.name,
        data: {
          loading: true,
        },
      })
      await entity.dispatch("search", {
        dataset,
        query,
        sort,
        size: size,
      });
    } finally {
      DatasetViewSettings.update({
        where: dataset.name,
        data: {
          loading: false,
        },
      })
    }

    const viewSettings = DatasetViewSettings.find(dataset.name);
    const newPagination = { size: size, page: 1 };
    displayQueryParams({
      query,
      sort,
      enableAnnotation: viewSettings.annotationEnabled,
      pagination: newPagination,
    });

    await Pagination.update({
      where: dataset.name,
      data: newPagination,
    });
    return entity.find(dataset.name);
  },

  async enableAnnotation(_, { dataset, value }) {
    displayQueryParams({
      query: dataset.query,
      sort: dataset.sort,
      enableAnnotation: value,
      pagination: dataset.viewSettings.pagination,
    });
    return await DatasetViewSettings.update({
      where: dataset.name,
      data: {
        annotationEnabled: value,
      },
    });
  },

  async paginate({ dispatch }, { dataset, size, page }) {
    const newPagination = await Pagination.update({
      where: dataset.name,
      data: {
        page: page,
        size: size,
      },
    });

    const newDataset = await dataset.constructor.update({
      where: dataset.name,
      data: {
        viewSettings: { ...dataset.viewSettings, pagination: newPagination },
      },
    });
    displayQueryParams({
      query: dataset.query,
      sort: dataset.sort,
      enableAnnotation: dataset.annotationEnabled,
      pagination: {
        ...newPagination,
        page,
        size,
      },
    });
    try {
      DatasetViewSettings.update({
        where: dataset.name,
        data: {
          loading: true,
        },
      })
      await dispatch(
        `entities/${toSnakeCase(dataset.task)}/paginate`,
        {
          dataset: newDataset,
          from: newPagination.from,
          size,
        },
        { root: true }
      );
    } finally {
      DatasetViewSettings.update({
        where: dataset.name,
        data: {
          loading: false,
        },
      })
    }
  },
};

export default {
  getters,
  actions,
};
