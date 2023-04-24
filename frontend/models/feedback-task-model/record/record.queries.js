import { Record as RecordModel } from "./Record.model";

// UPSERT
const upsertRecords = (records) => {
  RecordModel.insertOrUpdate({ data: records });
};

// GET
const getRecordWithFieldsAndResponsesByUserId = (
  datasetId,
  userId,
  recordIndex = 0
) => {
  return RecordModel.query()
    .with("record_fields")
    .with("record_responses", (query) => {
      query.where("user_id", userId);
    })
    .where("dataset_id", datasetId)
    .offset(recordIndex)
    .first();
};

// EXIST
const isRecordWithRecordIndexByDatasetIdExists = (datasetId, recordIndex) => {
  return RecordModel.query()
    .where("dataset_id", datasetId)
    .where("record_index", recordIndex)
    .exists();
};
const isRecordContainsAnyResponsesByUserId = (userId, recordId) => {
  return RecordModel.query()
    .whereId(recordId)
    .has("record_responses", (query) => {
      query.where("user_id", userId);
    })
    .exists();
};

export {
  upsertRecords,
  getRecordWithFieldsAndResponsesByUserId,
  isRecordWithRecordIndexByDatasetIdExists,
  isRecordContainsAnyResponsesByUserId,
};
