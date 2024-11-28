export interface DatasetExportSettings {
  name: string;
  subset?: string;
  split?: string;
  isPrivate: boolean;
  hfToken: string;
}
