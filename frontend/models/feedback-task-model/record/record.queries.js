import { Record as RecordModel } from "./Record.model";

const RECORD_STATUS = Object.freeze({
  PENDING: "PENDING",
  DISCARDED: "DISCARDED",
  SUBMITTED: "SUBMITTED",
});

// NOTE - IMPORTANT : in the backend, the status are in lowercase
const RESPONSE_STATUS_FOR_API = Object.freeze({
  MISSING: "missing",
  DISCARDED: "discarded",
  SUBMITTED: "submitted",
});

// UPSERT
const upsertRecords = (records) => {
  RecordModel.insertOrUpdate({ data: records });
};

// UPDATE
const updateRecordStatusByRecordId = (recordId, recordStatus) => {
  RecordModel.update({
    where: recordId,
    data: { record_status: recordStatus },
  });
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
    .where("record_index", recordIndex)
    .first();
};
const getRecordIndexByRecordId = (recordId) => {
  return RecordModel.query().whereId(recordId).first()?.record_index;
};
const getRecordStatusByDatasetIdAndRecordIndex = (datasetId, recordIndex) => {
  return RecordModel.query()
    .where("dataset_id", datasetId)
    .where("record_index", recordIndex)
    .first()?.record_status;
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

// DELETE
const deleteAllRecords = () => RecordModel.deleteAll();

export {
  RECORD_STATUS,
  RESPONSE_STATUS_FOR_API,
  upsertRecords,
  getRecordWithFieldsAndResponsesByUserId,
  getRecordStatusByDatasetIdAndRecordIndex,
  getRecordIndexByRecordId,
  updateRecordStatusByRecordId,
  isRecordWithRecordIndexByDatasetIdExists,
  isRecordContainsAnyResponsesByUserId,
  deleteAllRecords,
};
