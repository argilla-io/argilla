import { useResolve } from "ts-injecty";
import { Debounce } from "~/v1/infrastructure/services/useDebounce";
import { Queue } from "~/v1/infrastructure/services/useQueue";
import { DiscardRecordUseCase } from "~/v1/domain/usecases/discard-record-use-case";
import { Record } from "~/v1/domain/entities/record/Record";
import { TBeforeUnload } from "~/v1/infrastructure/services/useBeforeUnload";

export const useDiscard = (
  record: Record,
  beforeUnload: TBeforeUnload,
  debounce: Debounce,
  queue: Queue,
  { emit }
) => {
  const discardUseCase = useResolve(DiscardRecordUseCase);

  const onDiscard = async () => {
    if (record.isDiscarded) return;

    await discard(record);

    emit("on-discard-responses");
  };

  const discard = (record: Record) => {
    debounce.stop();
    beforeUnload.destroy();

    queue.enqueue(() => {
      return discardUseCase.execute(record);
    });
  };

  return { onDiscard };
};
