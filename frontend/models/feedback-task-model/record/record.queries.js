import { Record as RecordModel } from "./Record.model";

// UPSERT
const upsertRecords = (records) => {
  RecordModel.insertOrUpdate({ data: records });
};

// GET
const getRecordWithFieldsAndResponsesByDatasetId = (
  datasetId,
  numberOfRecord = 1,
  fromRecord = 0
) => {
  return RecordModel.query()
    .with("record_fields")
    .with("record_responses")
    .where("dataset_id", datasetId)
    .limit(numberOfRecord)
    .offset(fromRecord)
    .first();
};
export { upsertRecords, getRecordWithFieldsAndResponsesByDatasetId };
