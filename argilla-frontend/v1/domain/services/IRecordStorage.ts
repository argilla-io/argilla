import { Records } from "../entities/record/Records";

export interface IRecordStorage {
  save(records: Records);
  get(): Records;
}
