import { IRecordStorage } from "@/v1/domain/services/IRecordStorage";
import { useStoreFor } from "@/v1/store/create";
import { Records } from "@/v1/domain/entities/record/Records";

const useStoreForRecords = useStoreFor<Records, IRecordStorage>(Records);

export const useRecords = () => {
  const state = useStoreForRecords();

  const clearRecords = () => {
    state.save(new Records());
  };

  const add = (newRecords: Records) => {
    const oldRecords = state.get();

    const allRecords = [...oldRecords.records];

    newRecords.records.forEach((newRecord) => {
      const existingRecord = allRecords.findIndex(
        (record) => record.id === newRecord.id
      );

      if (existingRecord > 0) {
        allRecords[existingRecord] = newRecord;
      } else {
        allRecords.push(newRecord);
      }
    });

    state.save(new Records(allRecords, newRecords.total));
  };

  return {
    ...state,
    add,
    clearRecords,
  };
};
