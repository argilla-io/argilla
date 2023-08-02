import { Record as RecordModel } from "./Record.model";

const RECORD_STATUS = Object.freeze({
  PENDING: "PENDING",
  DISCARDED: "DISCARDED",
  SUBMITTED: "SUBMITTED",
});

const RECORD_STATUS_COLOR = Object.freeze({
  PENDING: "#b6b9ff",
  DISCARDED: "#c3c1c1",
  SUBMITTED: "#3e5cc9",
});

// NOTE - IMPORTANT : in the backend, the status are in lowercase
const RESPONSE_STATUS_FOR_API = Object.freeze({
  MISSING: "missing",
  DISCARDED: "discarded",
  SUBMITTED: "submitted",
});

// UPSERT
const upsertRecords = async (records) => {
  await RecordModel.insertOrUpdate({ data: records });
};

// UPDATE
const updateRecordStatusByRecordId = (recordId, recordStatus) => {
  RecordModel.update({
    where: recordId,
    data: { record_status: recordStatus },
  });
};

/**
 * @deprecated
 */
// GET
const getRecordWithFieldsSuggestionsAndResponsesByUserId = (
  datasetId,
  userId,
  recordIndex = 0
) => {
  return RecordModel.query()
    .with("record_fields")
    .with("record_responses", (query) => {
      query.where("user_id", userId);
    })
    .with("record_suggestions")
    .where("dataset_id", datasetId)
    .where("record_index", recordIndex)
    .first();
};
/**
 * @deprecated
 */
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

/**
 * @deprecated
 */
const isAnyRecordByDatasetId = (datasetId) => {
  return RecordModel.query().where("dataset_id", datasetId).exists();
};

// DELETE
const deleteAllRecords = async () => await RecordModel.deleteAll();

export {
  RECORD_STATUS,
  RECORD_STATUS_COLOR,
  RESPONSE_STATUS_FOR_API,
  upsertRecords,
  getRecordWithFieldsSuggestionsAndResponsesByUserId,
  getRecordStatusByDatasetIdAndRecordIndex,
  getRecordIndexByRecordId,
  updateRecordStatusByRecordId,
  isRecordWithRecordIndexByDatasetIdExists,
  isRecordContainsAnyResponsesByUserId,
  isAnyRecordByDatasetId,
  deleteAllRecords,
};
