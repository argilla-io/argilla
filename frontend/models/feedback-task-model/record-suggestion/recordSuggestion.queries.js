import { RecordSuggestion as RecordSuggestionModel } from "./RecordSuggestion.model";

// UPSERT
const upsertRecordSuggestions = (recordSuggestions) =>
  RecordSuggestionModel.insertOrUpdate({ data: recordSuggestions });

export { upsertRecordSuggestions };
