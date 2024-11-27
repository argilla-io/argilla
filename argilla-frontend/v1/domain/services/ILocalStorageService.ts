export type Options =
  | "showShortcutsHelper"
  | "layout"
  | "redirectTo"
  | "language"
  | "theme"
  | "datasetExportJobIds";

export interface ILocalStorageService {
  get(key: Options): any;
  set(key: Options, value: any): void;
  pop(key: Options): any;
}
