/*
 * coding=utf-8
 * Copyright 2021-present, the Recognai S.L. team.
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

import {
  ObservationDataset,
  USER_DATA_METADATA_KEY,
  getDatasetModelPrimaryKey,
} from "@/models/Dataset";
import { DatasetViewSettings, Pagination } from "@/models/DatasetViewSettings";
import { AnnotationProgress } from "@/models/AnnotationProgress";
import { currentWorkspace, NO_WORKSPACE } from "@/models/Workspace";
import { Base64 } from "js-base64";
import { TokenClassificationDataset } from "../../models/TokenClassification";
import { formatEntityIdForAnnotation } from "../../models/token-classification/TokenAnnotation.modelTokenClassification";
import { formatEntityIdForPrediction } from "../../models/token-classification/TokenPrediction.modelTokenClassification";
import { formatAnnotationPredictionid } from "../../models/token-classification/TokenRecord.modelTokenClassification";
import { formatEntityIdForRuleAnnotation } from "../../models/token-classification/TokenRuleAnnotation.modelTokenClassification";
import { formatDatasetIdForTokenGlobalEntityModel } from "../../models/token-classification/TokenGlobalEntity.modelTokenClassification";

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

async function _getOrFetchDataset({ workspace, name }) {
  /**
   * Find locally a dataset by its name and fetch from backend if not found
   */

  const inputForPrimaryKey = {
    owner: workspace,
    name,
  };
  const datasetPrimaryKey = getDatasetModelPrimaryKey(inputForPrimaryKey);
  let ds = ObservationDataset.find(datasetPrimaryKey);
  if (ds !== null) {
    return ds;
  }
  await ObservationDataset.api().get(`/datasets/${name}`, {
    dataTransformer: ({ data }) => {
      data.owner = data.owner || workspace;
      return data;
    },
  });

  ds = ObservationDataset.find(datasetPrimaryKey);

  return ds;
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
    await _refreshDatasetAggregations({ dataset: _dataset });
  }
  if (pagination && pagination.page > 1) {
    return await _paginate({
      dataset: _dataset,
      size: pagination.size,
      page: pagination.page,
    });
  }

  return _dataset;
}

async function _configureDatasetViewSettings(datasetName, viewMode) {
  /**
   * Initialize dataset view settings
   */
  // TODO: Maybe check if settings already exists
  await DatasetViewSettings.insert({
    data: {
      pagination: { id: datasetName },
      id: datasetName,
      viewMode: viewMode ? viewMode : "explore",
    },
  });
}

function _configuredRouteParams() {
  /**
   * Read the route query params: query, sort, viewMode and pagination
   */
  const { query, sort, viewMode, pagination } = $nuxt.$route.query;
  return {
    query: JSON.parse(query ? Base64.decode(query) : "{}"),
    sort: JSON.parse(sort ? Base64.decode(sort) : "[]"),
    viewMode: viewMode || "explore",
    pagination: pagination ? JSON.parse(Base64.decode(pagination)) : {},
  };
}

function _displayQueryParams({ query, sort, viewMode, pagination }) {
  /**
   * Set different route query params
   */

  // TODO: merge values. Allow partial definition

  $nuxt.$router.push({
    query: {
      ...$nuxt.$route.query,
      query: Base64.encodeURI(JSON.stringify(query)),
      sort: Base64.encodeURI(JSON.stringify(sort)),
      viewMode: viewMode,
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
  return await DatasetViewSettings.update({
    where: id,
    data: data,
  });
}

async function _callSearchApi({ dataset, query, sort, size, from = 0 }) {
  const { advancedQueryDsl } = $nuxt.$route.query;
  if (advancedQueryDsl === null || advancedQueryDsl === "true") {
    query.advanced_query_dsl = true;
  }
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
    return await _updateTaskDataset({ dataset, data: { results } });
  } finally {
    const { viewMode } = await _updateViewSettings({
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
      viewMode: viewMode,
      pagination,
    });
  }
}

async function _refreshDatasetAggregations({ dataset }) {
  const { aggregations } = await _querySearch({
    dataset,
    query: dataset.query,
    size: 0,
  });

  return await _updateTaskDataset({
    dataset,
    data: { results: { aggregations } },
  });
}

async function _search({ dataset, query, sort, size }) {
  query = _normalizeSearchQuery({ query: query || {}, dataset });
  sort = sort || dataset.sort || [];
  size = size || Pagination.find(dataset.name).size;
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
    viewMode: viewSettings.viewMode,
    pagination: { size, page },
  });

  const entity = dataset.getTaskDatasetClass();
  return entity
    .query()
    .withAllRecursive()
    .whereId(getDatasetModelPrimaryKey(dataset))
    .first();
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

  const updatedDataset = await entity.update({
    where: dataset.id.split("."),
    data: {
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

  if (persistBackend) {
    try {
      await _persistRecords({
        dataset,
        records,
      });
      _fetchAnnotationProgress(dataset);
    } catch (error) {
      await entity.update({
        where: dataset.id,
        data: dataset,
      });
    }
  }

  return updatedDataset;
}

async function _updateTaskDataset({ dataset, data }) {
  const datasetPrimaryKey = getDatasetModelPrimaryKey(dataset);

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

  const formatedDataset = {
    ...dataset,
    ...data,
    results: mergeObjectsDeep(datasetResults, dataResults),
  };

  await entity.insertOrUpdate({
    where: dataset.id,
    data: formatedDataset,
  });

  if (dataset.task === "TokenClassification") {
    const records = data.results ? data.results.records : null;
    if (records) {
      updateTokenRecordsByDatasetId(datasetPrimaryKey, records);
    }
  }

  return entity.find(datasetPrimaryKey);
}

const updateTokenRecordsByDatasetId = (datasetPrimaryKey, records) => {
  const tokenRecords = initTokenRecordsObjectForRecordsModel(
    datasetPrimaryKey,
    records
  );

  TokenClassificationDataset.insertOrUpdate({
    where: datasetPrimaryKey,
    data: {
      token_records: tokenRecords,
    },
  });
};

const initTokenGlobalEntitiesByDatasetId = (datasetPrimaryKey) => {
  const datasetId = formatDatasetIdForTokenGlobalEntityModel(datasetPrimaryKey);
  const formattedGlobalEntities = [];
  const { annotated_as, predicted_as } = TokenClassificationDataset.find(
    datasetPrimaryKey
  )?.results?.aggregations || { annotated_as: {}, predicted_as: {} };
  const concatPredictionsAndAnnotations = { ...annotated_as, ...predicted_as };

  Object.keys(concatPredictionsAndAnnotations).forEach((text, index) => {
    const entity = {
      dataset_id: datasetId,
      text,
      color_id: index,
      is_activate: false,
    };
    formattedGlobalEntities.push(entity);
  });

  TokenClassificationDataset.insertOrUpdate({
    where: datasetPrimaryKey,
    data: {
      token_global_entities: formattedGlobalEntities,
    },
  });
};

async function _updatePagination({ id, size, page }) {
  const pagination = await Pagination.update({
    where: id,
    data: { size, page },
  });

  return pagination;
}

const initTokenRecordsObjectForRecordsModel = (datasetPrimaryKey, records) => {
  const tokenRecords = records.map(
    (
      { id, search_keywords, status, tokens, text, annotation, prediction },
      recordIndex
    ) => {
      const formattedAnnotationPredictionid = formatAnnotationPredictionid(
        recordIndex,
        datasetPrimaryKey
      );

      const formatted_token_annotation = annotation
        ? formatAnnotationOrPredictionOrRuleAnnotation(
            "ANNOTATION",
            id,
            formattedAnnotationPredictionid,
            annotation
          )
        : null;

      const formatted_token_prediction = prediction
        ? formatAnnotationOrPredictionOrRuleAnnotation(
            "PREDICTION",
            id,
            formattedAnnotationPredictionid,
            prediction
          )
        : null;

      return {
        id,
        dataset_id: datasetPrimaryKey.join("."),
        search_keywords,
        status,
        tokens,
        text,
        prediction,
        token_annotation: formatted_token_annotation,
        token_prediction: formatted_token_prediction,
      };
    }
  );

  return tokenRecords;
};

const formatAnnotationOrPredictionOrRuleAnnotation = (
  entityType,
  record_id,
  recordIndex,
  { agent, entities }
) => {
  const FUNCTION_TO_FIRE = functionToFireToFormatTokenEntityId(entityType);

  return {
    id: recordIndex,
    agent: agent,
    record_id,
    token_entities: entities.map(({ label, start, end, score }, index) => {
      const idPrefix = `${record_id}_${start}_${end}`;
      return {
        id: FUNCTION_TO_FIRE ? FUNCTION_TO_FIRE(idPrefix) : index,
        record_id,
        agent,
        label,
        start,
        end,
        score,
      };
    }),
  };
};

const functionToFireToFormatTokenEntityId = (entityType) => {
  let FUNCTION_TO_FIRE = null;
  switch (entityType.toUpperCase()) {
    case "ANNOTATION":
      FUNCTION_TO_FIRE = formatEntityIdForAnnotation;
      break;
    case "PREDICTION":
      FUNCTION_TO_FIRE = formatEntityIdForPrediction;
      break;
    case "RULEANNOTATION":
      FUNCTION_TO_FIRE = formatEntityIdForRuleAnnotation;
      break;
    default:
      console.log("WARNING : The type from the entities are UNKNOWN");
  }
  return FUNCTION_TO_FIRE;
};

const getters = {
  findByName: () => (name) => {
    const workspace = currentWorkspace($nuxt.$route);
    const inputForPrimaryKey = {
      owner: workspace,
      name,
    };
    const datasetPrimaryKey = getDatasetModelPrimaryKey(inputForPrimaryKey);
    const ds = ObservationDataset.find(datasetPrimaryKey);
    if (ds === null) {
      throw Error("Not found dataset named " + name);
    }

    return ds
      .getTaskDatasetClass()
      .query()
      .withAllRecursive()
      .whereId(datasetPrimaryKey)
      .first();
  },
};

const actions = {
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
  async resetRecord(_, { dataset, record }) {
    return await _updateDatasetRecords({
      dataset,
      records: [
        {
          ...record,
          selected: false,
          status: "Default",
        },
      ],
      persistBackend: true,
    });
  },
  async resetAnnotations(_, { dataset, records }) {
    const newRecords = records.map((record) => ({
      ...record,
      annotation: null,
      selected: false,
      status: "Default",
    }));
    return _updateDatasetRecords({
      dataset,
      records: newRecords,
      persistBackend: true,
    });
  },
  async validateAnnotations(_, { dataset, records, agent }) {
    const newRecords = records.map((record) => ({
      ...record,
      annotation: {
        ...record.annotation,
        agent,
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
      where: dataset.id.split("."),
      data: {
        ...dataset,
        metadata: {
          ...dataset.metadata,
          ...metadata,
        },
      },
    });
  },

  async deleteDataset(_, { workspace, name }) {
    var url = `/datasets/${name}`;
    if (workspace !== NO_WORKSPACE) {
      url += `?workspace=${workspace}`;
    }
    const deleteResults = await ObservationDataset.api().delete(url, {
      delete: [workspace, name],
    });
    return deleteResults;
  },

  async refreshAnnotationProgress(_, dataset) {
    return await _fetchAnnotationProgress(dataset);
  },

  async fetchAll() {
    /**
     * Fetch all observation datasets from backend
     */

    return await ObservationDataset.api().get("/datasets/", {
      persistBy: "create",
      dataTransformer: ({ data }) => {
        return data.map((datasource) => {
          datasource.owner = datasource.owner || NO_WORKSPACE;
          return datasource;
        });
      },
    });
  },
  async fetchByName(_, name) {
    /**
     * Fetch a observation dataset by name
     */
    const workspace = currentWorkspace($nuxt.$route);
    const ds = await _getOrFetchDataset({ workspace, name });
    const { viewMode } = _configuredRouteParams();
    await _configureDatasetViewSettings(ds.name, viewMode);
    const dataset = await _loadTaskDataset(ds);
    await dataset.initialize();
    await _updateAnnotationProgress({
      id: name,
      total: dataset.globalResults.total,
      aggregations: dataset.globalResults.aggregations,
    });

    if (dataset.task === "TokenClassification") {
      const datasetPrimaryKey = getDatasetModelPrimaryKey(dataset);
      initTokenGlobalEntitiesByDatasetId(datasetPrimaryKey);
    }
    return dataset;
  },

  async search(_, { dataset, query, sort, size }) {
    return await _search({ dataset, query, sort, size });
  },

  async changeViewMode(_, { dataset, value }) {
    const settings = await _updateViewSettings({
      id: dataset.name,
      data: { viewMode: value, visibleRulesList: false },
    });

    _displayQueryParams({
      /**
       * Set different route query params
       */
      query: dataset.query,
      sort: dataset.sort,
      viewMode: value,
      pagination: Pagination.find(dataset.name),
    });

    return settings;
  },

  async paginate(_, { dataset, size, page }) {
    await _paginate({ dataset, size, page });
  },

  async resetSearch(_, { dataset, size }) {
    return await _search({
      dataset,
      query: {},
      sort: [
        {
          id: "status",
          key: "status",
          group: "Status",
          name: "Status",
          order: "desc",
        },
      ],
      size,
    });
  },

  async refresh(_, { dataset }) {
    const pagination = Pagination.find(dataset.name);
    const paginatedDataset = await _paginate({
      dataset,
      size: pagination.size,
      page: pagination.page,
    });
    await _refreshDatasetAggregations({ dataset: paginatedDataset });
    await _fetchAnnotationProgress(paginatedDataset);
  },
};

export default {
  getters,
  actions,
};
