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
import { AnnotationProgress } from "@/models/AnnotationProgress";
import { Base64 } from "js-base64";

const isObject = (obj) => obj && typeof obj === "object";

function initializeObjectDeep(object, defaultValue = 0) {
  const result = {};

  Object.keys(object).forEach((key) => {
    const oVal = object[key];

    if (isObject(oVal)) {
      result[key] = initializeObjectDeep(oVal);
    } else {
      result[key] = defaultValue;
    }
  });
  return result;
}

function mergeObjectsDeep(...objects) {
  return objects.reduce((prev, obj) => {
    Object.keys(obj).forEach((key) => {
      const pVal = prev[key];
      const oVal = obj[key];

      if (Array.isArray(pVal) && Array.isArray(oVal)) {
        prev[key] = oVal;
      } else if (isObject(pVal) && isObject(oVal)) {
        prev[key] = mergeObjectsDeep(pVal, oVal);
      } else {
        prev[key] = oVal;
      }
    });

    return prev;
  }, {});
}

async function _getOrFetchDataset(name) {
  /**
   * Find locally a dataset by its name and fetch from backend if not found
   */
  let ds = ObservationDataset.find(name);
  if (ds !== null) {
    return ds;
  }
  await ObservationDataset.api().get(`/datasets/${name}`);
  return await _getOrFetchDataset(name);
}

async function _fetchAnnotationProgress(dataset) {
  const { total, aggregations } = await _querySearch({
    dataset,
    query: {},
    size: 0,
  });

  return await _updateAnnotationProgress({
    id: dataset.name,
    total,
    aggregations,
  });
}

async function _loadTaskDataset(dataset) {
  /**
   * Loads a specific dataset for records observation
   */
  if (dataset.task === null) {
    throw Error("Wrong dataset task initialization");
  }

  const { query, sort, pagination } = _configuredRouteParams();
  let _dataset = await _search({
    dataset,
    query,
    sort,
    size: pagination.size,
  });

  const { total, aggregations } = _dataset.globalResults;
  if (total === undefined || aggregations === undefined) {
    const globalResults = await _querySearch({
      dataset: _dataset,
      query: {},
      size: 0,
    });

    _dataset = await _updateTaskDataset({
      dataset: _dataset,
      data: { globalResults },
    });
  }

  if (pagination && pagination.page > 1) {
    await _paginate({
      dataset: _dataset,
      size: pagination.size,
      page: pagination.page,
    });
  }

  return _dataset;
}

async function _configureDatasetViewSettings(
  datasetName,
  enableAnnotationMode
) {
  /**
   * Initialize dataset view settings
   */
  // TODO: Maybe check if settings already exists
  await DatasetViewSettings.insert({
    data: {
      pagination: { id: datasetName },
      id: datasetName,
      annotationEnabled: enableAnnotationMode === "true" ? true : false,
    },
  });
}

function _configuredRouteParams() {
  /**
   * Read the route query params: query, sort, allowAnnotation and pagination
   */
  const { query, sort, allowAnnotation, pagination } = $nuxt.$route.query;
  return {
    query: JSON.parse(query ? Base64.decode(query) : "{}"),
    sort: JSON.parse(sort ? Base64.decode(sort) : "[]"),
    allowAnnotation: allowAnnotation || false,
    pagination: pagination ? JSON.parse(Base64.decode(pagination)) : {},
  };
}

function _displayQueryParams({ query, sort, enableAnnotation, pagination }) {
  /**
   * Set different route query params
   */

  // TODO: merge values. Allow partial definition

  $nuxt.$router.push({
    query: {
      query: Base64.encodeURI(JSON.stringify(query)),
      sort: Base64.encodeURI(JSON.stringify(sort)),
      allowAnnotation: enableAnnotation,
      pagination: Base64.encodeURI(JSON.stringify(pagination)),
    },
  });
}

function _normalizeSearchQuery({ query, dataset }) {
  /**
   * Prepare a query merging query params and already stored dataset query params
   */
  const metadata = { ...(dataset.query || {}).metadata, ...query.metadata };
  Object.keys(metadata).forEach((key) => {
    if (metadata[key].length <= 0) {
      delete metadata[key];
    }
  });

  if (query.predicted === false) {
    query.predicted = undefined;
  }

  if (Array.isArray(query.predicted)) {
    if (query.predicted.length > 1) {
      query.predicted = undefined;
    } else {
      query.predicted = query.predicted[0];
    }
  }

  return Object.keys(query).length === 0
    ? {}
    : { ...dataset.query, ...query, metadata };
}

async function _updateViewSettings({ id, data }) {
  /**
   * Wraps view settings updates
   */
  await DatasetViewSettings.update({
    where: id,
    data: data,
  });
}

async function _callSearchApi({ dataset, query, sort, size, from = 0 }) {
  const { response } = await ObservationDataset.api().post(
    `/datasets/${dataset.name}/${dataset.task}:search?limit=${size}&from=${from}`,
    {
      query: { ...query, query_text: query.text },
      sort,
    },
    {
      save: false,
    }
  );
  return response.data;
}

async function _querySearch({ dataset, query, sort, size }) {
  const save = size == 0 ? false : true;
  const results = await _callSearchApi({ dataset, query, sort, size });
  if (save) {
    await _updateTaskDataset({ dataset, data: { results, query, sort } });
  }
  return results;
}

async function _paginate({ dataset, size, page }) {
  const pagination = new Pagination({ size, page });

  try {
    await _updateViewSettings({ id: dataset.name, data: { loading: true } });
    const results = await _callSearchApi({
      dataset,
      query: dataset.query,
      sort: dataset.sort,
      size,
      from: pagination.from,
    });
    await _updateTaskDataset({ dataset, data: { results } });
  } finally {
    await _updateViewSettings({
      id: dataset.name,
      data: { loading: false },
    });
    await _updatePagination({
      id: dataset.name,
      size,
      page,
    });
    _displayQueryParams({
      /**
       * Set different route query params
       */
      query: dataset.query,
      sort: dataset.sort,
      enableAnnotation: dataset.annotationEnabled,
      pagination,
    });
  }
}

async function _search({ dataset, query, sort, size }) {
  query = _normalizeSearchQuery({ query: query || {}, dataset });
  sort = sort || dataset.sort || [];
  size = size || new Pagination().size;

  try {
    await _updateViewSettings({ id: dataset.name, data: { loading: true } });
    await _querySearch({ dataset, query, sort, size });
  } finally {
    await _updateViewSettings({ id: dataset.name, data: { loading: false } });
  }

  const viewSettings = DatasetViewSettings.find(dataset.name);
  const { page } = await _updatePagination({
    id: dataset.name,
    size,
    page: 1,
  });

  _displayQueryParams({
    /**
     * Set different route query params
     */
    query,
    sort,
    enableAnnotation: viewSettings.annotationEnabled,
    pagination: { size, page },
  });

  const entity = dataset.getTaskDatasetClass();
  return entity.find(dataset.name);
}

async function _updateAnnotationProgress({ id, total, aggregations }) {
  return await AnnotationProgress.insertOrUpdate({
    data: {
      id,
      total,
      validated: aggregations.status.Validated,
      discarded: aggregations.status.Discarded,
      annotatedAs: aggregations.annotated_as,
    },
  });
}

async function _persistRecords({ dataset, records }) {
  await ObservationDataset.api().post(
    `/datasets/${dataset.name}/${dataset.task}:bulk`,
    {
      records,
    },
    {
      save: false,
    }
  );
}

async function _updateDatasetRecords({
  dataset,
  records,
  persistBackend = false,
}) {
  if (records.length === 0) {
    return;
  }
  let aggregations = {};
  const entity = dataset.getTaskDatasetClass();
  if (persistBackend) {
    await _persistRecords({
      dataset,
      records,
    });
    _fetchAnnotationProgress(dataset);
  }

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
}

async function _updateTaskDataset({ dataset, data }) {
  const entity = dataset.getTaskDatasetClass();
  const { globalResults, results } = data;

  let datasetResults = dataset.$toJson().results || {};
  let dataResults = results || {};

  if (globalResults && globalResults.aggregations) {
    datasetResults.aggregations = globalResults.aggregations;
  }

  if (dataResults && dataResults.aggregations) {
    datasetResults.aggregations = initializeObjectDeep(
      datasetResults.aggregations || {}
    );
  }

  await entity.insertOrUpdate({
    where: dataset.name,
    data: {
      ...dataset,
      ...data,
      results: mergeObjectsDeep(datasetResults, dataResults),
    },
  });
  return entity.find(dataset.name);
}

async function _updatePagination({ id, size, page }) {
  const pagination = await Pagination.update({
    where: id,
    data: { size, page },
  });

  return pagination;
}

const getters = {
  findByName: () => (name) => {
    const ds = ObservationDataset.find(name);
    if (ds === null) {
      throw Error("Not found dataset named " + name);
    }

    return ds
      .getTaskDatasetClass()
      .query()
      .withAllRecursive()
      .whereId(name)
      .first();
  },
};

const actions = {
  async editAnnotations(_, { dataset, records }) {
    const newRecords = records.map((record) => ({
      ...record,
      selected: false,
      status: "Edited",
    }));
    return await _updateDatasetRecords({
      dataset,
      records: newRecords,
      persistBackend: true,
    });
  },
  async updateDatasetRecords(_, { dataset, records }) {
    return await _updateDatasetRecords({
      dataset,
      records,
    });
  },
  async discardAnnotations(_, { dataset, records }) {
    const newRecords = records.map((record) => ({
      ...record,
      selected: false,
      status: "Discarded",
    }));
    await _updateDatasetRecords({
      dataset,
      records: newRecords,
      persistBackend: true,
    });
  },
  async validateAnnotations(_, { dataset, records, agent }) {
    const newRecords = records.map((record) => ({
      ...record,
      annotation: {
        agent,
        ...record.annotation,
      },
      selected: false,
      status: "Validated",
    }));
    return _updateDatasetRecords({
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
    const deleteResults = await ObservationDataset.api().delete(
      `/datasets/${name}`,
      {
        delete: name,
      }
    );
    return deleteResults;
  },

  async refreshAnnotationProgress(_, dataset) {
    return await _fetchAnnotationProgress(dataset);
  },

  async fetchAll() {
    /**
     * Fetch all observation datasets from backend
     */
    return await ObservationDataset.api().get("/datasets/");
  },
  async fetchByName(_, name) {
    /**
     * Fetch a observation dataset by name
     */
    const ds = await _getOrFetchDataset(name);
    const { allowAnnotation } = _configuredRouteParams();
    await _configureDatasetViewSettings(ds.name, allowAnnotation);
    const dataset = await _loadTaskDataset(ds);
    await _updateAnnotationProgress({
      id: name,
      total: dataset.globalResults.total,
      aggregations: dataset.globalResults.aggregations,
    });

    return dataset;
  },

  async load(_, dataset) {
    return await _loadTaskDataset(dataset);
  },

  async search(_, { dataset, query, sort, size }) {
    return await _search({ dataset, query, sort, size });
  },

  async enableAnnotation(_, { dataset, value }) {
    const settings = await _updateViewSettings({
      id: dataset.name,
      data: { annotationEnabled: value },
    });

    _displayQueryParams({
      /**
       * Set different route query params
       */
      query: dataset.query,
      sort: dataset.sort,
      enableAnnotation: value,
      pagination: Pagination.find(dataset.name),
    });

    return settings;
  },

  async paginate(_, { dataset, size, page }) {
    await _paginate({ dataset, size, page });
  },
};

export default {
  getters,
  actions,
};
