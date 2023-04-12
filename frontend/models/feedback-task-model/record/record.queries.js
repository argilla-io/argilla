import { Record as RecordModel } from "./Record.model";

// UPSERT
const upsertRecords = (records) => {
  RecordModel.insertOrUpdate({ data: records });
};

export { upsertRecords };
