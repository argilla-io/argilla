import { useResolve } from "ts-injecty";
import { ClearRecordUseCase } from "~/v1/domain/usecases/clear-record-use-case";
import { Debounce } from "~/v1/infrastructure/services/useDebounce";
import { Queue } from "~/v1/infrastructure/services/useQueue";
import { Record } from "~/v1/domain/entities/record/Record";
import { TBeforeUnload } from "~/v1/infrastructure/services/useBeforeUnload";

export const useClear = (
  record: Record,
  beforeUnload: TBeforeUnload,
  debounce: Debounce,
  queue: Queue
) => {
  const clearUseCase = useResolve(ClearRecordUseCase);

  const onClear = async () => {
    await clear(record);
  };

  const clear = (record: Record) => {
    debounce.stop();
    beforeUnload.destroy();

    queue.enqueue(() => {
      return clearUseCase.execute(record);
    });
  };

  return { onClear };
};
