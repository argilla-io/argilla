import { RecordField as RecordFieldModel } from "./RecordField.model";

// DELETE ALL FIELDS
const deleteAllRecordFields = () => RecordFieldModel.deleteAll();

export { deleteAllRecordFields };
