interface MetadataTermsSettings {
  type: "terms";
  values?: string[];
}
interface MetadataIntegerSettings {
  type: "integer";
  min?: number;
  max?: number;
}

interface MetadataFloatSettings {
  type: "float";
  min?: number;
  max?: number;
}

export interface BackendMetadata {
  id: string;
  name: string;
  title: string;
  settings:
    | MetadataTermsSettings
    | MetadataIntegerSettings
    | MetadataFloatSettings;
  visible_for_annotators: boolean;
  dataset_id: string;
}

export interface BackendMetadataMetric {
  id: string;
  type: "terms" | "integer" | "float";
  total: number;
  values: { term: string; count: number }[];
  min?: number;
  max?: number;
}
