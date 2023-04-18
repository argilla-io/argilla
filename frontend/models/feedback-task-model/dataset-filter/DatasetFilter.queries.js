import { DatasetFilter as DatasetFilterModel } from "./DatasetFilter.model";

// UPSERT
const upsertDatasetFilters = (globalFilters) => {
  console.log("vvvv", globalFilters);
  DatasetFilterModel.insertOrUpdate({ data: globalFilters });
};

// GET
const getFiltersByDatasetId = (datasetId) => {
  return DatasetFilterModel.query().where("dataset_id", datasetId).get();
};

export { upsertDatasetFilters, getFiltersByDatasetId };
