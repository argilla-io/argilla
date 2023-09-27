interface MetadataTermsSettings {
  type: "terms";
  values?: string[];
}
interface MetadataIntegerSettings {
  type: "integer";
}

interface MetadataFloatSettings {
  type: "float";
}

export interface BackendMetadata {
  id: string;
  name: string;
  description: string;
  settings:
    | MetadataTermsSettings
    | MetadataIntegerSettings
    | MetadataFloatSettings;
}
