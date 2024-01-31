import { Dictionary } from "../entities/common/Params";

export interface RouterService {
  getQuery(): Dictionary<string | (string | null)[]>;
  go(where: string, external: boolean): void;
}
