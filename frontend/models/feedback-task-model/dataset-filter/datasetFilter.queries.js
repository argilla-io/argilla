import { DatasetFilter as DatasetFilterModel } from "./DatasetFilter.model";

const SIDEBAR_GROUP = Object.freeze({
  METRICS: "METRICS",
  MODE: "MODE",
  REFRESH: "REFRESH",
});

// UPSERT
const upsertDatasetFilters = (globalFilters) => {
  DatasetFilterModel.insertOrUpdate({ data: globalFilters });
};

// GET
const getFiltersByDatasetId = (
  datasetId,
  orderBy = "order",
  ascendent = true
) => {
  const direction = ascendent ? "asc" : "desc";
  return DatasetFilterModel.query()
    .where("dataset_id", datasetId)
    .orderBy(orderBy, direction)
    .get();
};

export { upsertDatasetFilters, getFiltersByDatasetId, SIDEBAR_GROUP };
