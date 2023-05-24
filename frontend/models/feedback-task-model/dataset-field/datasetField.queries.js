import { DatasetField as DatasetFieldModel } from "./DatasetField.model";

// GET
const getFieldsByDatasetId = (
  datasetId,
  orderBy = "order",
  ascendent = true
) => {
  const direction = ascendent ? "asc" : "desc";

  return DatasetFieldModel.query()
    .where("dataset_id", datasetId)
    .orderBy(orderBy, direction)
    .get();
};

// UPSERT
const upsertDatasetFields = (globalFields) => {
  DatasetFieldModel.insertOrUpdate({ data: globalFields });
};

export { getFieldsByDatasetId, upsertDatasetFields };
