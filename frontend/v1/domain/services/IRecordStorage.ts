import { Records } from "../entities/record/Records";

export interface IRecordStorage {
  add(records: Records);
  get(): Records;
}
