// GET
const URL_GET_WORKSPACES = `/workspaces`;
const URL_GET_V1_DATASETS = `/v1/me/datasets`;

// DELETE
const urlDeleteDatasetV1 = (datasetId) => `/v1/datasets/${datasetId}`;

export { URL_GET_WORKSPACES, URL_GET_V1_DATASETS, urlDeleteDatasetV1 };
