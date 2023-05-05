// GET
const URL_GET_WORKSPACES = `/workspaces`;
const URL_GET_V1_DATASETS = `/v1/me/datasets`;
const urlGetListOfDatasetRecords = (
  datasetId,
  recordOffset,
  numberOfRecordsToFetch
) =>
  `/v1/me/datasets/${datasetId}/records?include=responses&offset=${recordOffset}&limit=${numberOfRecordsToFetch}`;

// POST
const urlCreateRecordResponses = (recordId) =>
  `/v1/records/${recordId}/responses`;

// DELETE
const urlDeleteDatasetV1 = (datasetId) => `/v1/datasets/${datasetId}`;

export {
  URL_GET_WORKSPACES,
  URL_GET_V1_DATASETS,
  urlGetListOfDatasetRecords,
  urlDeleteDatasetV1,
  urlCreateRecordResponses,
};
