import { Progress } from "../entities/dataset/Progress";

export interface ITeamProgressStorage {
  save(progress: Progress);
}
