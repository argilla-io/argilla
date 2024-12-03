export default {
  multi_label_selection: "Multi-label",
  ranking: "Ranking",
  label_selection: "Label",
  span: "Span",
  text: "Text",
  image: "Image",
  rating: "Rating",
  minimize: "Minimize",
  select: "Select",
  search: "Search",
  searchPlaceholder: "Introduce a query",
  searchDatasets: "Search datasets",
  share: "Share",
  expand: "Expand",
  copied: "Copied",
  copiedToClipboard: "Copied to clipboard",
  copyLink: "Copy link",
  copyRecord: "Copy record",
  refresh: "Refresh",
  typeYourText: "Type your text",
  all: "All",
  value: "Value",
  title: "Title",
  description: "Description",
  labels: "Labels",
  order: "Order",
  useMarkdown: "Use Markdown",
  suggestionFirst: "Show suggestions first",
  visibleForAnnotators: "Visible for annotators",
  recordInfo: "Record info",
  viewMetadata: "View metadata",
  allowExtraMetadata: "Allow extra metadata",
  extraMetadata: "Extra metadata",
  dimension: "Dimension",
  visibleLabels: "Visible labels",
  annotationGuidelines: "Annotation guidelines",
  guidelines: "Guidelines",
  taskDistribution: "Task distribution",
  minimumSubmittedResponses: "Minimum submitted responses",
  taskDistributionTooltip:
    "A task is complete when all records have the \nminimum number of submitted responses",
  noAnnotationGuidelines: "This dataset has no annotation guidelines",
  required: "Required",
  optional: "Optional",
  template: "Template",
  rows: "rows",
  noRecordsMessages: {
    datasetEmptyForAnnotator:
      "The dataset is empty. Ask an administrator to upload records and come back soon.",
    datasetEmptyForAdmin:
      "The dataset is empty. You can add records using the Python SDK, see <a href='https://docs.argilla.io/latest/how_to_guides/record/'>documentation</a> on adding records.",
    taskDistributionCompleted: "🎉 The task is completed!",
    noSubmittedRecords: "You have not submitted any record yet",
    noRecordsFound: "You have no {status} records matching your query",
    noRecords: "You have no {status} records",
    noPendingRecordsToAnnotate: "🎉 Your have no pending records to annotate",
    noDraftRecordsToReview: "You have no draft records to review",
  },
  couldNotLoadImage: "Could not load image",
  breadcrumbs: {
    home: "Home",
    datasetSettings: "settings",
    userSettings: "My settings",
  },
  datasets: {
    left: "left",
    completed: "Completed",
    pending: "Pending",
  },
  recordStatus: {
    pending: "pending",
    draft: "draft",
    discarded: "discarded",
    submitted: "submitted",
    validated: "validated",
    completedTooltip:
      "The record is complete, it has the \nminimum number of responses",
  },
  userSettings: {
    title: "My settings",
    fields: {
      userName: "Username",
      firstName: "Name",
      lastName: "Surname",
      workspaces: "Workspaces",
    },
    apiKey: "API key",
    apiKeyDescription:
      "API key tokens allow you to manage datasets using the Python SDK.",
    theme: "Theme",
    language: "Language",
    copyKey: "Copy key",
  },
  userAvatarTooltip: {
    settings: "My settings",
    docs: "View docs",
    logout: "Log out",
  },
  settings: {
    title: "Dataset settings",
    datasetInfo: "Dataset info",
    seeYourDataset: "See your dataset",
    editFields: "Edit fields",
    editQuestions: "Edit questions",
    editMetadata: "Edit metadata properties",
    editVectors: "Edit vectors",
    deleteDataset: "Delete dataset",
    deleteWarning: "Be careful, this action is not reversible",
    deleteConfirmation: "Delete confirmation",
    deleteConfirmationMessage:
      "You are about to delete: <strong>{datasetName}</strong> from workspace <strong>{workspaceName}</strong>. This action cannot be undone",
    yesDelete: "Yes, delete",
    write: "Write",
    preview: "Preview",
    uiPreview: "UI Preview",
  },
  button: {
    ignore_and_continue: "Ignore and continue",
    login: "Sign in",
    "hf-login": "Sign in with Hugging Face",
    sign_in_with_username: "Sign in with username",
    cancel: "Cancel",
    continue: "Continue",
    delete: "Delete",
    tooltip: {
      copyToClipboard: "Copy to clipboard",
      copyNameToClipboard: "Copy dataset name to clipboard",
      copyLinkToClipboard: "Copy dataset link to clipboard",
      goToDatasetSettings: "Go to dataset settings",
      datasetSettings: "Dataset settings",
    },
  },
  to_submit_complete_required: "To submit complete \nrequired responses",
  some_records_failed_to_annotate: "Some records failed to annotate",
  changes_no_submit: "You didn't submit your changes",
  bulkAnnotation: {
    recordsSelected: "1 record selected | {count} records selected",
    recordsViewSettings: "Record size",
    fixedHeight: "Collapse records",
    defaultHeight: "Expand records",
    to_annotate_record_bulk_required: "No record selected",
    select_to_annotate: "Select all",
    pageSize: "Page size",
    selectAllResults: "Select all {total} matched records",
    haveSelectedRecords: "You have selected all {total} records",
    actionConfirmation: "Bulk action confirmation",
    actionConfirmationText:
      "This action will affect {total} records, do you want to continue? ",
    allRecordsAnnotated: "The {total} records have been {action}",
    affectedAll: {
      submitted: "submitted",
      discarded: "discarded",
      draft: "saved as draft",
    },
  },
  shortcuts: {
    label: "Shortcuts",
    pagination: {
      go_to_previous_record: "Previous (←)",
      go_to_next_record: "Next (→)",
    },
  },
  questions_form: {
    validate: "Validate",
    clear: "Clear",
    reset: "Reset",
    discard: "Discard",
    submit: "Submit",
    draft: "Save as draft",
    write: "Write",
  },
  sorting: {
    label: "Sort",
    addOtherField: "+ Add another field",
    suggestion: {
      score: "Suggestion score",
      value: "Suggestion value",
    },
    response: "Response value",
    record: "general",
    metadata: "metadata",
  },
  suggestion: {
    agent: "\nagent: {agent}",
    score: "\nscore: {score}",
    tooltip: "This question contains a suggestion {agent} {score}",
    filter: {
      value: "Suggestion values",
      score: "Score",
      agent: "Agent",
    },
    plural: "Suggestions",
    name: `Suggestion`,
  },
  similarity: {
    "record-number": "Record number",
    findSimilar: "Find similar",
    similarTo: "Similar to",
    similarityScore: "Similarity Score",
    similarUsing: "similar using",
    expand: "Expand",
    collapse: "Collapse",
  },
  spanAnnotation: {
    shortcutHelper: "Hold 'Shift' to select character level",
    notSupported: "Span annotation is not supported for your browser",
    searchLabels: "Search labels",
  },
  login: {
    title: "Sign in",
    username: "Username",
    usernameDescription: "Enter your username",
    password: "Password",
    show: "Show",
    hide: "Hide",
    passwordDescription: "Enter your password",
    claim: "Work on data together.</br>Make your models better.",
    error: "Wrong username or password. Try again",
    hf: {
      title: "Welcome to {space}",
      subtitle: "Join <strong>{user}</strong> to build better datasets for AI",
    },
  },
  of: "of",
  status: "Status",
  filters: "Filters",
  filterBy: "Filter by...",
  fields: "Fields",
  field: "Field",
  questions: "Questions",
  general: "General",
  metadata: "Metadata",
  vectors: "Vectors",
  dangerZone: "Danger zone",
  responses: "Responses",
  "reset-all": "Reset all",
  reset: "Reset",
  less: "Less",
  learnMore: "Learn more",
  with: "with",
  find: "Find",
  cancel: "Cancel",
  focus_mode: "Focus view",
  bulk_mode: "Bulk view",
  update: "Update",
  youAreOnlineAgain: "You are online again",
  youAreOffline: "You are offline",
  write: "Write",
  preview: "Preview",
  metrics: {
    total: "Total",
    progress: {
      default: "Progress",
      my: "My Progress",
      team: "Team progress",
    },
  },
  home: {
    zeroDatasetsFound: "0 datasets found",
    argillaDatasets: "Your datasets",
    none: "None yet",
    importTitle: "Import a dataset from Hugging Face Hub",
    importText:
      "Start with a dataset from the Hub by simply pasting the repository name",
    importButton: "Import dataset",
    importFromHub: "Import dataset from Hugging Face",
    importFromPython: "Import from Python",
    importFromPythonHFWarning:
      "If you're using a private Space, check the <a target='_blank' href='https://docs.argilla.io/latest/getting_started/how-to-configure-argilla-on-huggingface/#how-to-use-private-spaces'>docs</a>.",
    exampleDatasetsTitle: "Don’t know where to start?",
    exampleDatasetsText: "Explore these example datasets",
    guidesTitle: "Not familiar with Argilla?",
    guidesText: "Take a look at these guides:",
    pasteRepoIdPlaceholder: "Paste a repo id e.g., stanfordnlp/imdb",
    demoLink:
      "Log into this <a href='https://huggingface.co/spaces/argilla/argilla-template-space' target='_blank'>demo</a> to try Argilla out",
    name: "Dataset name",
    updatedAt: "Updated",
    createdAt: "Created",
  },
  datasetCreation: {
    questions: {
      labelSelection: {
        atLeastTwoOptions: "At least two options are required",
        optionsWithoutLabel: "Empty options are not allowed",
        optionsSeparatedByComma: "Use comma to separate labels",
      },
      rating: {
        atLeastTwoOptions: "At least two options are required",
      },
      span: {
        fieldRelated: "One text field is required",
      },
    },
    atLeastOneQuestion: "At least one question is required.",
    atLeastOneRequired: "At least one required question is needed.",
    hasInvalidQuestions: "Some questions are invalid",
    createDataset: "Create the dataset in Argilla",
    datasetName: "Dataset name",
    name: "Name",
    assignWorkspace: "Assign a workspace",
    selectSplit: "Select a split",
    recordWarning:
      "The created dataset will include the first 10K rows and further records can be logged via the python SDK.",
    button: "Create dataset",
    fields: "Fields",
    questionsTitle: "Questions",
    yourQuestions: "Your questions",
    requiredField: "Required field",
    requiredQuestion: "Required question",
    select: "Select",
    mapToColumn: "Map to column",
    applyToaAField: "Annotate spans on:",
    subset: "Subset",
    selectSubset: "Your can create a dataset from only one subset.",
    preview: "Preview",
    importData: "Import data",
    addRecords: "Add records",
    cantLoadRepository: "Dataset not found or available on Hugging Face",
    none: "None",
    noWorkspaces:
      "Please, follow this <a target='_blank' href='https://docs.argilla.io/latest/how_to_guides/workspace/#create-a-new-workspace'>guide</a> to create a workspace",
  },
  config: {
    field: {
      text: "Text field",
      chat: "Chat field",
      image: "Image field",
      "no mapping": "No mapping",
    },
    question: {
      text: "Text",
      rating: "Rating",
      label_selection: "Label",
      ranking: "Ranking",
      multi_label_selection: "Multi-label",
      span: "Span",
      "no mapping": "No mapping",
    },
    questionId: {
      text: "text",
      rating: "rating",
      label_selection: "label",
      ranking: "ranking",
      multi_label_selection: "multi-label",
      span: "span",
    },
  },
  persistentStorage: {
    adminOrOwner:
      "Persistent storage is not enabled. All data will be lost if this space restarts. Go to the space settings to enable it.",
    annotator:
      "Persistent storage is not enabled. All data will be lost if this space restarts.",
  },
  colorSchema: {
    system: "System",
    light: "Light",
    dark: "Dark",
    "high-contrast": "High contrast",
  },
  validations: {
    businessLogic: {
      missing_vector: {
        message: "Vector not found for the selected record",
      },
      update_distribution_with_existing_responses: {
        message:
          "Distribution settings can't be modified for a dataset containing user responses",
      },
    },
    http: {
      401: {
        message: "Could not validate credentials",
      },
      404: {
        message: "Could not find the requested resource",
      },
      429: {
        message: "Please wait a few seconds before trying again",
      },
      500: {
        message: "An error occurred, please try again later",
      },
    },
  },
};
