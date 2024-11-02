import { RecordCriteria } from "../../record/RecordCriteria";

export const createBasicRecordCriteria = () =>
  new RecordCriteria(
    "FAKE_DATASET_ID",
    "1",
    "pending",
    "FAKE_SEARCH_TEXT",
    "",
    "",
    "",
    "",
    ""
  );
