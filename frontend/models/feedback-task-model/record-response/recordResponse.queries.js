import { RecordResponse as RecordResponseModel } from "./RecordResponse.model";

// GET
const getRecordResponsesByRecordId = ({ userId, recordId }) => {
  return RecordResponseModel.query()
    .where("record_id", recordId)
    .where("user_id", userId)
    .get();
};
const getRecordResponsesIdByRecordId = ({ userId, recordId }) => {
  return RecordResponseModel.query()
    .where("record_id", recordId)
    .where("user_id", userId)
    .first()?.id;
};
const findRecordResponseByRecordIdByQuestionId = ({ recordId, questionId }) => {
  return RecordResponseModel.query().whereId([questionId, recordId]).first();
};

// UPSERT
const upsertRecordResponses = (recordResponses) =>
  RecordResponseModel.insertOrUpdate({ data: recordResponses });

// DELETE
const deleteRecordResponsesByUserIdAndResponseId = (userId, responseId) =>
  RecordResponseModel.delete((recordResponse) => {
    return (
      userId === recordResponse.user_id && responseId === recordResponse.id
    );
  });

// EXIST
const isResponsesByUserIdExists = (userId, recordId) =>
  RecordResponseModel.query()
    .where("user_id", userId)
    .where("record_id", recordId)
    .exists();

export {
  getRecordResponsesByRecordId,
  getRecordResponsesIdByRecordId,
  findRecordResponseByRecordIdByQuestionId,
  upsertRecordResponses,
  deleteRecordResponsesByUserIdAndResponseId,
  isResponsesByUserIdExists,
};
