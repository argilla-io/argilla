import { useStoreFor } from "@/v1/store/create";
import { Progress } from "~/v1/domain/entities/dataset/Progress";
import { ITeamProgressStorage } from "~/v1/domain/services/ITeamProgressStorage";

const useStoreTeamProgress = useStoreFor<Progress, ITeamProgressStorage>(
  Progress
);
export const useTeamProgress = () => useStoreTeamProgress();
