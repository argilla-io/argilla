import { useResolve } from "ts-injecty";
import { onBeforeMount } from "vue-demi";
import { GetDatasetProgressUseCase } from "~/v1/domain/usecases/get-dataset-progress-use-case";
import {
  useEvents,
  UpdateTeamProgressEventHandler,
} from "~/v1/infrastructure/events";
import { useTeamProgress } from "~/v1/infrastructure/storage/TeamProgressStorage";

interface TeamProgressProps {
  datasetId: string;
}

export const useTeamProgressViewModel = (props: TeamProgressProps) => {
  const { state: progress } = useTeamProgress();
  const getDatasetProgress = useResolve(GetDatasetProgressUseCase);

  onBeforeMount(() => {
    useEvents(UpdateTeamProgressEventHandler);

    getDatasetProgress.execute(props.datasetId);
  });

  return {
    progress,
  };
};
