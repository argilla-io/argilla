export interface BackendEnvironment {
  argilla: {
    show_huggingface_space_persistent_storage_warning: boolean;
  };
  huggingface: {
    space_id: string;
    space_title: string;
    space_subdomain: string;
    space_host: string;
    space_repo_name: string;
    space_author_name: string;
    space_persistent_storage_enabled: boolean;
  };
}
