import { RecordField as RecordFieldModel } from "./RecordField.model";

// DELETE ALL FIELDS
const deleteAllRecordFields = async () => await RecordFieldModel.deleteAll();

export { deleteAllRecordFields };
