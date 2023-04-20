import { Record as RecordModel } from "./Record.model";

// UPSERT
const upsertRecords = (records) => {
  RecordModel.insertOrUpdate({ data: records });
};

// GET
const getRecordWithFieldsByDatasetId = (
  datasetId,
  recordIndex = 0
) => {
  return RecordModel.query()
    .with("record_fields")
    .where("dataset_id", datasetId)
    .offset(recordIndex)
    .first();
};
export { upsertRecords, getRecordWithFieldsByDatasetId };
