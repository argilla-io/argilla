import { Records } from "../entities/record/Records";

export interface IRecordStorage {
  append(records: Records);
  replace(records: Records);
  get(): Records;
}
