import { RecordResponse as RecordResponseModel } from "./RecordResponse.model";

// GET
const getRecordResponsesByRecordId = ({ userId, recordId }) => {
  return RecordResponseModel.query()
    .where("record_id", recordId)
    .where("user_id", "daboudi")
    .get();
};
const findRecordResponseByRecordIdByQuestionId = ({ recordId, questionId }) => {
  return RecordResponseModel.query().whereId([questionId, recordId]).first();
};

// UPSERT
const upsertRecordResponses = (recordResponses) =>
  RecordResponseModel.insertOrUpdate({ data: recordResponses });

export {
  getRecordResponsesByRecordId,
  findRecordResponseByRecordIdByQuestionId,
  upsertRecordResponses,
};
