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

import _ from "lodash";
import { ObservationDataset, USER_DATA_METADATA_KEY } from "@/models/Dataset";
import { DatasetViewSettings, Pagination } from "@/models/DatasetViewSettings";
import {
  updateLoadingState,
  getShortcutChars,
} from "@/models/viewSettings.queries";
import { AnnotationProgress } from "@/models/AnnotationProgress";
import { currentWorkspace } from "@/models/Workspace";
import { Base64 } from "js-base64";
import { Vector as VectorModel } from "@/models/Vector";
import {
  upsertLabelsInGlobalLabelModel,
  deleteAllGlobalLabelModel,
} from "@/models/globalLabel.queries";
import { Notification } from "@/models/Notifications";
import {
  upsertNewGlobalLabel,
  getAllLabelsTextByDatasetId,
  isLabelTextExistInGlobalLabel,
  isLabelTextExistInGlobalLabelAndSavedInBack,
} from "@/models/globalLabel.queries";
import { getDatasetFromORM } from "@/models/dataset.utilities";

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

  let ds = ObservationDataset.find([workspace, name]);
  if (ds !== null) {
    return ds;
  }
  await ObservationDataset.api().get(`/datasets/${name}`, {
    dataTransformer: ({ data }) => {
      data.workspace = data.workspace || workspace;
      return data;
    },
  });
  return await _getOrFetchDataset({ workspace, name });
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
      viewMode: getViewMode(viewMode),
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
    viewMode: getViewMode(viewMode),
    pagination: pagination ? JSON.parse(Base64.decode(pagination)) : {},
  };
}

function getViewMode(viewMode) {
  return viewMode || "annotate";
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

  const vector = VectorModel.query().where("is_active", true).first();

  const numberOfRecords = vector ? 50 : size;

  const { record_id, vector_name, vector_values } = vector || {};
  const newQueryText = queryFactoryForSearchCall(record_id, query.text);
  const newQuery = {
    ...query,
    query_text: newQueryText,
    vector: vector
      ? {
          name: vector_name,
          value: vector_values,
        }
      : null,
  };

  const { response } = await ObservationDataset.api().post(
    `/datasets/${dataset.name}/${dataset.task}:search?limit=${numberOfRecords}&from=${from}`,
    {
      query: { ...newQuery },
      sort,
    },
    {
      save: false,
    }
  );
  return response.data;
}

const queryFactoryForSearchCall = (recordReferenceId, queryText) => {
  let newQueryText = queryText;
  let recordIdToExcludeText = null;
  if (!_.isNil(recordReferenceId)) {
    recordIdToExcludeText = `NOT id:"${recordReferenceId}"`;
    newQueryText = queryTextCurryFactory(queryText || "")(
      recordIdToExcludeText
    )();
  } else {
    // nothing
  }

  return newQueryText;
};

const queryTextCurryFactory = (queryText1) => (queryText2) =>
  queryText2 === undefined
    ? queryText1
    : queryTextCurryFactory(
        `${queryText1} ${queryText1.length ? "AND" : ""} ${queryText2}`.trim()
      );

async function _querySearch({ dataset, query, sort, size }) {
  const save = size == 0 ? false : true;
  const results = await _callSearchApi({
    dataset,
    query,
    sort,
    size,
  });
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
  return entity.query().withAllRecursive().whereId(dataset.id).first();
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
    where: dataset.id,
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
    where: dataset.id,
    data: {
      ...dataset,
      ...data,
      results: mergeObjectsDeep(datasetResults, dataResults),
    },
  });
  return entity.find(dataset.id);
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
    const workspace = currentWorkspace($nuxt.$route);
    const ds = ObservationDataset.find([workspace, name]);
    if (ds === null) {
      throw Error("Not found dataset named " + name);
    }

    return ds
      .getTaskDatasetClass()
      .query()
      .withAllRecursive()
      .whereId(ds.id)
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
      where: dataset.id,
      data: {
        ...dataset,
        metadata: {
          ...dataset.metadata,
          ...metadata,
        },
      },
    });
  },
  async onAddNewLabels(context, { datasetId, datasetTask, newLabels }) {
    const { name: datasetName } = getDatasetFromORM(datasetId, datasetTask);

    if (datasetName && datasetTask) {
      const labelsbeforeAddNewLabel = getAllLabelsTextByDatasetId(datasetId);

      const isSomeNewLabelNotInGlobalLabels =
        checkIfSomeNewLabelNotInGlobalLabels(datasetId, newLabels);

      const isSomeNewLabelNotSavedInBack = checkIfSomeNewLabelNotSavedInBack(
        datasetId,
        newLabels
      );

      if (isSomeNewLabelNotInGlobalLabels || isSomeNewLabelNotSavedInBack) {
        try {
          const labels = [
            ...new Set([...labelsbeforeAddNewLabel, ...newLabels]),
          ];
          await context.dispatch("onSaveDatasetSettings", {
            datasetName,
            datasetTask,
            labels,
          });

          // NOTE - delete then init globalLabels to update shortcuts by labels
          deleteAllGlobalLabelModel();
          labels.forEach((newLabel) => {
            upsertNewGlobalLabel({
              datasetId,
              datasetName,
              newLabel,
              isActivate: false,
              isSavedInBack: true,
            });
          });
        } catch (err) {
          const { response } = err;
          if (response === TYPE_OF_FEEDBACK.NOT_ALLOWED_TO_UPDATE_LABELS) {
            console.log(
              "The user is not allowed to update dataset settings labels"
            );
          } else {
            throw new Error("Error on adding new labels");
          }
        }
      } else {
        Notification.dispatch("notify", {
          message: `The labels <b>"${newLabels}"</b> already exist in the list of labels`,
          type: "info",
        });
      }
    } else {
      console.error(
        `Could not find dataset with name:${datasetName} and task:${datasetTask}`
      );
    }
  },
  async onSaveDatasetSettings(context, { datasetName, datasetTask, labels }) {
    let message = "";
    let typeOfNotification = "";
    let statusCall = null;
    try {
      const data = { label_schema: { labels } };
      await ObservationDataset.api().patch(
        `/datasets/${datasetName}/${datasetTask}/settings`,
        data
      );

      message = "The Labels are updated!";
      typeOfNotification = "success";
    } catch (err) {
      const { status } = err.response;
      message = `STATUS:${status} The labels of the dataset ${datasetName} with task ${datasetTask} could not be saved`;
      typeOfNotification = "error";
      statusCall = status;
      if (status === 403) {
        throw { response: TYPE_OF_FEEDBACK.NOT_ALLOWED_TO_UPDATE_LABELS };
      }
    } finally {
      statusCall === 403 ||
        Notification.dispatch("notify", {
          message,
          type: typeOfNotification,
        });
    }
  },
  async deleteDataset(_, { workspace, name: datasetName }) {
    let message = "";
    let typeOfNotification = "";
    let statusCall = null;

    let url = `/datasets/${datasetName}`;
    url += `?workspace=${workspace}`;
    try {
      await ObservationDataset.api().delete(url, {
        delete: [workspace, datasetName],
      });
      message = `${datasetName} have been deleted`;
      typeOfNotification = "success";
    } catch ({ response }) {
      let { status } = response;
      statusCall = status;
      message = `It is not possible to delete ${datasetName}`;
      typeOfNotification = "error";
      if (status === 403) {
        throw { response: TYPE_OF_FEEDBACK.NOT_ALLOWED_TO_UPDATE_LABELS };
      }
    } finally {
      statusCall === 403 ||
        Notification.dispatch("notify", {
          message,
          type: typeOfNotification,
        });
    }
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

    const datasetTask = dataset.task;
    if (datasetTask === "TextClassification") {
      await fetchByNameForTextClassification(dataset);
    } else if (datasetTask === "TokenClassification") {
      await fetchByNameForTokenClassification(dataset);
    } else if (datasetTask === "Text2Text") {
      await fetchByNameForText2Text(dataset);
    }

    return dataset;
  },

  async load(_, dataset) {
    return await _loadTaskDataset(dataset);
  },

  async search(_, { dataset, query, sort, size }) {
    const searchResponse = await _search({
      dataset,
      query,
      sort,
      size,
    });
    const records = searchResponse.results?.records;
    initVectorModel(dataset.id, records);
    return searchResponse;
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
    const datasetPaginate = await _paginate({ dataset, size, page });

    const records = datasetPaginate.results?.records;
    initVectorModel(dataset.id, records);
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

    const records = paginatedDataset.results?.records;
    initVectorModel(dataset.id, records);
  },
};

const fetchByNameForTextClassification = async (dataset) => {
  //TODO - remove this function from this file  && put rules in dedicated ORM table
  await fetchAllRulesAndInsertRulesInTextClassificationORM(dataset);

  await formatLabelsAndInitGlobalLabelsORM(dataset);

  await _updateAnnotationProgress({
    id: dataset.name,
    total: dataset.globalResults.total,
    aggregations: dataset.globalResults.aggregations,
  });
  const records = dataset.results?.records;

  //TODO - next line => labels to remove when will use only initGlobalLabels(dataset) (dataset update with settings)
  const { labels } = await dataset.fetchMetricSummary("dataset_labels");

  const isMultiLabel = records.some((r) => r.multi_label);
  const entity = dataset.getTaskDatasetClass();
  await entity.insertOrUpdate({
    where: dataset.id,
    data: {
      workspace: dataset.workspace,
      name: dataset.name,
      _labels: labels,
      isMultiLabel,
    },
  });
  initVectorModel(dataset.id, records);
};

const fetchByNameForTokenClassification = async (dataset) => {
  await formatLabelsAndInitGlobalLabelsORM(dataset);

  await _updateAnnotationProgress({
    id: dataset.name,
    total: dataset.globalResults.total,
    aggregations: dataset.globalResults.aggregations,
  });
  const records = dataset.results?.records;
  initVectorModel(dataset.id, records);
};

const fetchByNameForText2Text = async (dataset) => {
  await _updateAnnotationProgress({
    id: name,
    total: dataset.globalResults.total,
    aggregations: dataset.globalResults.aggregations,
  });

  const records = dataset.results?.records;
  initVectorModel(dataset.id, records);
};

const initVectorModel = (datasetId, records) => {
  const isDatasetContainsAnyVectors = isAnyKeyInArrayItem(records, "vectors");
  if (isDatasetContainsAnyVectors) {
    const datasetJoinedId = datasetId.join(".");
    const vectorsData = formatVectorsToInsertInModel(datasetJoinedId, records);
    insertDataInVectorModel(vectorsData);
  }
};

const formatVectorsToInsertInModel = (datasetId, records) => {
  const vectorsData = [];
  records.forEach(({ id: recordId, vectors }) => {
    const vectorsByRecord = getVectorsByRecord(datasetId, recordId, vectors);
    vectorsData.push(...vectorsByRecord);
  });
  return vectorsData;
};

const getVectorsByRecord = (datasetId, recordId, vectors) => {
  const vectorsByToInsertInModel = [];
  Object.entries(vectors).forEach(([vectorName, { value: vectorValues }]) => {
    vectorsByToInsertInModel.push({
      dataset_id: datasetId,
      record_id: recordId,
      vector_name: vectorName,
      vector_values: vectorValues,
    });
  });
  return vectorsByToInsertInModel;
};

const insertDataInVectorModel = (vectors) => {
  VectorModel.insertOrUpdate({
    data: vectors,
  });
};

const isAnyKeyInArrayItem = (arrayWithObjItem, key) => {
  const isKeyInItem = (item) => item[key] && Object.keys(item[key]).length;
  return arrayWithObjItem.some(isKeyInItem);
};

const initGlobalLabels = async (
  { id, name: datasetName },
  labels,
  isLabelsSavedInBack
) => {
  deleteAllGlobalLabelModel();

  const joinedDatasetId = id.join(".");
  const formattedLabels = factoryLabelsForGlobalLabelsModel(
    joinedDatasetId,
    datasetName,
    labels,
    isLabelsSavedInBack
  );
  upsertLabelsInGlobalLabelModel(formattedLabels);
};

const fetchLabelsFromSettings = async ({ name, task }) => {
  try {
    let labelsResponse = null;
    await ObservationDataset.api().get(`/datasets/${name}/${task}/settings`, {
      validateStatus: validateStatusForSettings,
      dataTransformer: ({ data }) => {
        const { label_schema } = data;
        labelsResponse = label_schema?.labels || [];
      },
    });
    if (labelsResponse.length === 0) {
      throw { response: TYPE_OF_FEEDBACK.LABEL_SCHEMA_IS_EMPTY };
    }
    return labelsResponse;
  } catch (err) {
    if (err.response === TYPE_OF_FEEDBACK.LABEL_SCHEMA_IS_EMPTY) {
      console.log(`This dataset does not contains any settings`);
      throw { response: TYPE_OF_FEEDBACK.LABEL_SCHEMA_IS_EMPTY };
    }
    const { status } = err.response;
    throw new Error(`STATUS: ${status}, Could not fetch settings`);
  }
};

const formatLabelsAndInitGlobalLabelsORM = async (dataset) => {
  const { name: datasetName } = dataset;
  try {
    updateLoadingState(datasetName, true);
    const { labelsToInsertInORM, isLabelSavedInLabelSchema } =
      await factoryLabelsToInsertInGlobalModelORM(dataset);

    initGlobalLabels(dataset, labelsToInsertInORM, isLabelSavedInLabelSchema);
  } catch (err) {
    console.log(err);
  } finally {
    updateLoadingState(datasetName, false);
  }
};

const factoryLabelsToInsertInGlobalModelORM = async (dataset) => {
  let labelsToInsertInORM = null;
  let isLabelSavedInLabelSchema = false;
  try {
    const labels = await fetchLabelsFromSettings(dataset);
    labelsToInsertInORM = labels;
    isLabelSavedInLabelSchema = true;
  } catch (err) {
    if (err.response === TYPE_OF_FEEDBACK.LABEL_SCHEMA_IS_EMPTY) {
      const { labels } = await dataset.fetchMetricSummary("dataset_labels");
      labelsToInsertInORM =
        factoryAggregationLabelsForGlobalLabelsModel(labels);
      isLabelSavedInLabelSchema = false;
    }
  }
  return { labelsToInsertInORM, isLabelSavedInLabelSchema };
};

const factoryLabelsForGlobalLabelsModel = (
  datasetId,
  datasetName,
  labels,
  isSavedInBack = false
) => {
  const shortcuts = getShortcutChars(datasetName);
  const shortcutsLength = shortcuts.length;

  const formattedLabels = labels.map(({ id, name }, index) => {
    return {
      id: id,
      order: index,
      text: name,
      dataset_id: datasetId,
      color_id: index,
      shortcut: index < shortcutsLength ? String(shortcuts[index]) : null,
      is_saved_in_back: isSavedInBack,
    };
  });
  return formattedLabels;
};

const factoryAggregationLabelsForGlobalLabelsModel = (
  aggregationsLabelsModel
) => {
  return (
    aggregationsLabelsModel?.map((label) => {
      return { id: label, name: label };
    }) ?? []
  );
};

const fetchAllRulesAndInsertRulesInTextClassificationORM = async (dataset) => {
  if (!dataset.labelingRules) {
    await dataset.refreshRules();
  }
};

const checkIfSomeNewLabelNotInGlobalLabels = (datasetId, newLabels) => {
  const isNewLabelsNotInGlobalLabelsByItem = newLabels.map(
    (newLabel) => !isLabelTextExistInGlobalLabel(datasetId, newLabel)
  );

  const isSomeNewLabelNotInGlobalLabels =
    isNewLabelsNotInGlobalLabelsByItem.some((value) => value);

  return isSomeNewLabelNotInGlobalLabels;
};

const checkIfSomeNewLabelNotSavedInBack = (datasetId, newLabels) => {
  const isNewLabelsNotSavedInBack = newLabels.map(
    (newLabel) =>
      !isLabelTextExistInGlobalLabelAndSavedInBack(datasetId, newLabel)
  );

  const isSomeNewLabelNotSavedInBack = isNewLabelsNotSavedInBack.some(
    (value) => value
  );

  return isSomeNewLabelNotSavedInBack;
};

const validateStatusForSettings = (status) => {
  if (status >= 200 && status <= 400) return true;
  else if (status === 404) return true;
};

const TYPE_OF_FEEDBACK = Object.freeze({
  LABEL_SCHEMA_IS_EMPTY: "LABEL_SCHEMA_IS_EMPTY",
  NOT_ALLOWED_TO_UPDATE_LABELS: "NOT_ALLOWED_TO_UPDATE_LABELS",
});

export default {
  getters,
  actions,
};
