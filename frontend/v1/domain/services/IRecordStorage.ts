import { RecordStatus } from "../entities/record/RecordAnswer";
import { Records } from "../entities/record/Records";

export interface IRecordStorage {
  append(records: Records, onQueue: RecordStatus);
  replace(records: Records);
  save(records: Records);
  get(): Records;
}
