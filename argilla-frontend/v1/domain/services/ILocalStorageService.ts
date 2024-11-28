export type Options =
  | "showShortcutsHelper"
  | "layout"
  | "redirectTo"
  | "language"
  | "theme"
  | "datasetExportJobIds";

export interface ILocalStorageService {
  get<T>(key: Options): T;
  set<T>(key: Options, value: T): void;
  pop<T>(key: Options): T;
}
