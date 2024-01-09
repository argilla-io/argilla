export interface BackendUpdateDataset {
  guidelines?: string;
  allow_extra_metadata: boolean;
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
