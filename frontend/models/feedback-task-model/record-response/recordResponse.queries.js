import { RecordResponse as RecordResponseModel } from "./RecordResponse.model";

// GET
const getRecordResponsesByRecordId = (recordId) => {
  return RecordResponseModel.query().where("record_id", recordId).get();
};
const findRecordResponseByRecordIdByQuestionId = ({ recordId, questionId }) => {
  return RecordResponseModel.query().whereId([questionId, recordId]).first();
};

export {
  getRecordResponsesByRecordId,
  findRecordResponseByRecordIdByQuestionId,
};
