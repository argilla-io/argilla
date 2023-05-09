import { DatasetField as DatasetFieldModel } from "./DatasetField.model";

// UPSERT
const upsertDatasetFields = (globalFields) => {
  DatasetFieldModel.insertOrUpdate({ data: globalFields });
};

export { upsertDatasetFields };
