import { RecordResponse as RecordResponseModel } from "./RecordResponse.model";

// GET
const getRecordResponsesByRecordId = ({ userId, recordId }) => {
  return RecordResponseModel.query()
    .where("record_id", recordId)
    .where("user_id", userId)
    .get();
};
const findRecordResponseByRecordIdByQuestionId = ({ recordId, questionId }) => {
  return RecordResponseModel.query().whereId([questionId, recordId]).first();
};

export {
  getRecordResponsesByRecordId,
  findRecordResponseByRecordIdByQuestionId,
};
