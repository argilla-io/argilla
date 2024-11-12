import { useResolve } from "ts-injecty";
import { ref } from "vue";
import { GetFirstRecordFromHub } from "~/v1/domain/usecases/get-first-record-from-hub";

export const useDatasetConfiguration = () => {
  const firstRecord = ref(null);
  const getFirstRecordUseCase = useResolve(GetFirstRecordFromHub);

  const getFirstRecord = async (dataset: any) => {
    firstRecord.value = await getFirstRecordUseCase.execute(dataset);
  };

  return {
    firstRecord,
    getFirstRecord,
  };
};
