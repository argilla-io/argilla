export interface RouterService {
  go(where: string, params: { external: boolean; newWindow: boolean }): void;
}
