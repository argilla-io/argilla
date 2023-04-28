import { DatasetFilter as DatasetFilterModel } from "./DatasetFilter.model";

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

export { upsertDatasetFilters, getFiltersByDatasetId };
