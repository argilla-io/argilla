import { IRecordStorage } from "@/v1/domain/services/IRecordStorage";
import { useStoreFor } from "@/v1/store/create";
import { Records } from "@/v1/domain/entities/record/Records";

const useStoreForRecords = useStoreFor<Records, IRecordStorage>(Records);

export const useRecords = () => {
  const state = useStoreForRecords();

  const append = (newRecords: Records) => {
    const records = state.get();

    records.append(newRecords);

    state.save(records);
  };

  const replace = (newRecords: Records) => {
    state.save(newRecords);
  };

  return {
    ...state,
    append,
    replace,
  };
};
