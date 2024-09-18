export interface BackendDataset {
  id: string;
  name: string;
  guidelines: string;
  status: string;
  workspace_id: string;
  allow_extra_metadata: boolean;
  distribution: {
    strategy: string;
    min_submitted: number;
  };
  inserted_at: string;
  updated_at: string;
  last_activity_at: string;
}

export interface BackendDatasetWithWorkspace extends BackendDataset {
  workspace_name: string;
}

export interface BackendUpdateDataset {
  guidelines?: string;
  allow_extra_metadata: boolean;
  distribution: {
    strategy: string;
    min_submitted: number;
  };
}

export interface BackendDatasetFeedbackTaskResponse {
  guidelines: string;
  id: string;
  inserted_at: string;
  name: string;
  status: string;
  updated_at: string;
  last_activity_at: string;
  workspace_id: string;
}

export interface BackendProgress {
  total: number;
  completed: number;
  pending: number;
}
