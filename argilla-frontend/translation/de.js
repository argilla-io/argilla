export default {
  multi_label_selection: "Multi-Label",
  ranking: "Ranking",
  label_selection: "Label",
  span: "Bereich",
  text: "Text",
  image: "Bild",
  rating: "Bewertung",
  minimize: "Minimieren",
  select: "Auswählen",
  search: "Suchen",
  searchPlaceholder: "Suchbegriff eingeben",
  searchDatasets: "Datensätze durchsuchen",
  expand: "Erweitern",
  copied: "Kopiert",
  copyLink: "Link kopieren",
  copyRecord: "Eintrag kopieren",
  refresh: "Aktualisieren",
  typeYourText: "Geben Sie Ihren Text ein",
  all: "Alle",
  value: "Wert",
  title: "Titel",
  description: "Beschreibung",
  labels: "Labels",
  order: "Reihenfolge",
  useMarkdown: "Verwende Markdown",
  suggestionFirst: "Vorschlag zuerst",
  visibleForAnnotators: "Sichtbar für Annotatoren",
  recordInfo: "Eintragsinformationen",
  viewMetadata: "Metadaten ansehen",
  allowExtraMetadata: "Erlaube zusätzliche Metadaten",
  extraMetadata: "Zusätzliche Metadaten",
  dimension: "Dimension",
  visibleLabels: "Sichtbare Labels",
  annotationGuidelines: "Annotationsrichtlinien",
  guidelines: "Richtlinien",
  taskDistribution: "Annotationsverteilung",
  minimumSubmittedResponses:
    "Erforderliche Mindestanzahl an eingereichten Antworten",
  taskDistributionTooltip:
    "Eine Aufgabe ist abgeschlossen, wenn alle Datensätze die \nMindestanzahl an eingereichten Antworten haben.",
  noAnnotationGuidelines: "Dieser Datensatz hat keine Annotationsrichtlinien",
  required: "Erforderlich",
  optional: "Optional",
  template: "Template",
  noRecordsMessages: {
    datasetEmptyForAnnotator:
      "Der Datensatz ist leer. Bitten Sie einen Administrator, Daten hochzuladen, und versuchen Sie es später erneut.",
    datasetEmptyForAdmin:
      "Der Datensatz ist leer. Sie können Datensätze mit dem Python SDK hinzufügen. Siehe <a href='https://docs.argilla.io/latest/how_to_guides/record/'>Dokumentation</a> zum Hinzufügen von Einträgen.",
    taskDistributionCompleted: "🎉 Die Aufgabe ist erledigt!",
    noSubmittedRecords: "Sie haben noch keinen Datensatz eingereicht",
    noRecordsFound:
      "Sie haben keine {status} Datensätze, welche Ihrer Anfrage entsprechen",
    noRecords: "Sie haben keine {status} Datensätze",
    noPendingRecordsToAnnotate: "🎉 Die Aufgabe ist erledigt!",
    noDraftRecordsToReview: "Sie haben keine Entwürfe zu prüfen",
  },
  couldNotLoadImage: "Bild konnte nicht geladen werden",
  breadcrumbs: {
    home: "Start",
    datasetSettings: "Einstellungen",
    userSettings: "Meine Einstellungen",
  },
  datasets: {
    left: "übrig",
    completed: "Vollendet",
    pending: "Ausstehend",
  },
  recordStatus: {
    pending: "ausstehend",
    draft: "entwurf",
    discarded: "verworfen",
    submitted: "gesichert",
    validated: "validiert",
    completedTooltip:
      "Der Datensatz ist abgeschlossen, es hat die Anzahl der Antworten.",
  },
  userSettings: {
    title: "Meine Einstellungen",
    fields: {
      userName: "Benutzername",
      firstName: "Vorname",
      lastName: "Nachname",
      workspaces: "Arbeitsbereiche",
    },
    apiKey: "API-Key",
    apiKeyDescription:
      "API-Keys erlauben es die Datensätze über das Python SDK zu verwalten.",
    theme: "Theme",
    language: "Sprache",
    copyKey: "API-Key kopieren",
  },
  userAvatarTooltip: {
    settings: "Meine Einstellungen",
    docs: "Dokumentation ansehen",
    logout: "Abmelden",
  },
  settings: {
    title: "Datensatz-Einstellungen",
    datasetInfo: "Datensatz-Informationen",
    seeYourDataset: "Gehe zum Datensatz",
    editFields: "Felder bearbeiten",
    editQuestions: "Fragen bearbeiten",
    editMetadata: "Metadaten bearbeiten",
    editVectors: "Vektoren bearbeiten",
    deleteDataset: "Datensatz löschen",
    deleteWarning: "Seien Sie vorsichtig, diese Aktion ist nicht umkehrbar",
    deleteConfirmation: "Bestätigung der Löschung",
    deleteConfirmationMessage:
      "Sie sind dabei diesen Datensatz: <strong>{datasetName}</strong> aus dem Arbeitsbereich <strong>{workspaceName}</strong> zu löschen. Diese Aktion kann nicht rückgängig gemacht werden.",
    yesDelete: "Ja, löschen",
    write: "Bearbeiten",
    preview: "Vorschau",
    uiPreview: "UI Vorschau",
  },
  button: {
    ignore_and_continue: "Ignorieren und fortfahren",
    login: "Anmelden",
    signin_with_provider: "Anmeldung bei {provider} starten",
    "hf-login": "Mit Hugging Face anmelden",
    sign_in_with_username: "Mit Benutzername anmelden",
    cancel: "Abbrechen",
    continue: "Fortfahren",
    delete: "Löschen",
    tooltip: {
      copyToClipboard: "In Zwischenablage kopieren",
      copyNameToClipboard: "Datensatznamen in die Zwischenablage kopieren",
      copyLinkToClipboard: "Datensatzlink in die Zwischenablage kopieren",
      goToDatasetSettings: "Zu den Datensatzeinstellungen gehen",
      datasetSettings: "Datensatzeinstellungen",
    },
  },
  to_submit_complete_required:
    "Zum Absenden beantworten \nSie die benötigten Fragen",
  some_records_failed_to_annotate:
    "Einige Einträge konnten nicht annotiert werden",
  changes_no_submit: "Sie haben Ihre Änderungen nicht gespeichert",
  bulkAnnotation: {
    recordsSelected: "1 Eintrag ausgewählt | {count} Einträge ausgewählt",
    recordsViewSettings: "Anzahl der Einträge",
    fixedHeight: "Einträge zusammenklappen",
    defaultHeight: "Einträge erweitern",
    to_annotate_record_bulk_required: "Kein Eintrag ausgewählt",
    select_to_annotate: "Alles auswählen",
    pageSize: "Seitengröße",
    selectAllResults: "Alle {total} Einträge auswählen",
    haveSelectedRecords: "Sie haben alle {total} Einträge ausgewählt",
    actionConfirmation: "Mehrfach-Aktion bestätigen",
    actionConfirmationText:
      "Diese Aktion wird {total} Einträge ändern, wollen Sie fortfahren?",
    allRecordsAnnotated: "{total} Einträge wurden {action}",
    affectedAll: {
      submitted: "abgesendet",
      discarded: "verworfen",
      draft: "als Entwurf gespeichert",
    },
  },
  shortcuts: {
    label: "Tastenkürzel",
    pagination: {
      go_to_previous_record: "Vorheriges (←)",
      go_to_next_record: "Nächstes (→)",
    },
  },
  questions_form: {
    validate: "Validieren",
    clear: "Löschen",
    reset: "Zurücksetzen",
    discard: "Verwerfen",
    submit: "Absenden",
    draft: "Entwurf speichern",
    write: "Schreiben",
  },
  sorting: {
    label: "Sortieren",
    addOtherField: "+ Ein weiteres Feld hinzufügen",
    suggestion: {
      score: "Vorschlagsbewertung",
      value: "Vorschlagswert",
    },
    response: "Antwortwert",
    record: "allgemein",
    metadata: "Metadaten",
  },
  suggestion: {
    agent: "\nAgent: {agent}",
    score: "\nBewertung: {score}",
    tooltip: "Diese Frage enthält einen Vorschlag {agent} {score}",
    filter: {
      value: "Vorschlagswerte",
      score: "Bewertung",
      agent: "Agent",
    },
    plural: "Vorschläge",
    name: `Vorschlag`,
  },
  similarity: {
    "record-number": "Eintrag-Nummer",
    findSimilar: "Ähnliche Einträge finden",
    similarTo: "Ähnlich zu",
    similarityScore: "Ähnlichkeitsbewertung",
    similarUsing: "ähnlich unter Verwendung von",
    expand: "Erweitern",
    collapse: "Zusammenklappen",
  },
  spanAnnotation: {
    shortcutHelper: "Halten Sie 'Shift' gedrückt, um Zeichenebene auszuwählen",
    notSupported: "Bereichsannotation wird von Ihrem Browser nicht unterstützt",
    searchLabels: "Label finden",
  },
  login: {
    title: "Anmelden",
    username: "Benutzername",
    usernameDescription: "Geben Sie Ihren Benutzernamen ein",
    password: "Passwort",
    show: "Anzeigen",
    hide: "Ausblenden",
    passwordDescription: "Geben Sie ihr Passwort ein",
    claim: "Gemeinsames Arbeiten an Daten.</br>Verbessern Sie Ihre Modelle.",
    error: "Falscher Benutzername oder Passwort. Versuchen Sie es erneut",
    hf: {
      title: "Willkommen bei {space}",
      subtitle:
        "Helfe <strong>{user}</strong> bessere Datensätze für KI zu erstellen",
    },
  },
  of: "von",
  status: "Status",
  filters: "Filter",
  filterBy: "Filter nach...",
  fields: "Felder",
  questions: "Fragen",
  general: "Übersicht",
  metadata: "Metadaten",
  vectors: "Vektoren",
  dangerZone: "Gefahrenzone",
  responses: "Antworten",
  "reset-all": "Alle zurücksetzen",
  reset: "Zurücksetzen",
  less: "Weniger",
  learnMore: "Erfahre mehr",
  with: "mit",
  find: "Finden",
  cancel: "Abbrechen",
  focus_mode: "Fokusansicht",
  bulk_mode: "Massenansicht",
  update: "Aktualisieren",
  youAreOnlineAgain: "Sie sind wieder online",
  youAreOffline: "Sie sind offline",
  write: "Schreiben",
  preview: "Vorschau",
  datasetTable: {
    name: "Datensatz",
    workspace: "Arbeitsbereich",
    createdAt: "Erstellt am",
    lastActivityAt: "Aktualisiert am",
    progress: "Teamfortschritt",
  },
  metrics: {
    total: "Total",
    progress: {
      my: "mein Fortschritt",
      team: "Fortschritte im Team",
    },
  },
  home: {
    argillaDatasets: "Argilla Datensätze",
    none: "Bis jetzt keine",
    importTitle: "Importiere ein Datensatz aus dem Hugging Face Hub",
    importText:
      "Starten Sie mit einem Datensatz aus dem Hub, indem Sie einfach den Repository-Namen einfügen",
    importButton: "Datensatz importieren",
    importFromHub: "Direkt vom Hub importieren",
    importFromPython: "Mit Python importieren",
    importFromPythonHFWarning:
      "Wenn Sie einen privaten Space verwenden, lesen Sie die <a target='_blank' href='https://docs.argilla.io/latest/getting_started/how-to-configure-argilla-on-huggingface/#how-to-use-private-spaces'>Dokumentation</a>.",
    exampleDatasetsTitle: "Sie wissen nicht, wo Sie anfangen sollen?",
    exampleDatasetsText: "Erkunden Sie diese Beispiel-Datensätze",
    guidesTitle: "Nicht mit Argilla vertraut?",
    guidesText: "Nutzen Sie diese Anleitungen an:",
    pasteRepoIdPlaceholder: "Fügen Sie eine Repo-ID ein",
    demoLink:
      "Melden Sie sich bei dieser <a href='https://huggingface.co/spaces/argilla/argilla-template-space' target='_blank'>Demo</a> an, um Argilla auszuprobieren",
  },
  datasetCreation: {
    questions: {
      labelSelection: {
        atLeastTwoOptions: "Mindestens zwei Optionen müssen vorhanden sein",
        optionsWithoutLabel: "Optionen ohne Label sind nicht erlaubt",
        optionsSeparatedByComma: "Optionen müssen durch Kommas getrennt sein",
      },
    },
    atLeastOneQuestion: "Mindestens eine Frage wird benötigt",
    atLeastOneRequired: "Mindestens eine erforderliche Frage wird benötigt",
    hasInvalidQuestions: "Einige Fragen sind ungültig",
    createDataset: "Datensatz in Argilla erstellen",
    datasetName: "Name des Datensatzes",
    name: "Name",
    assignWorkspace: "Einem Workspace zuweisen",
    selectSplit: "Einen Datensatz-Split auswählen",
    recordWarning:
      "Der erstellte Datensatz wird nur die ersten 10Tsd Zeilen enthalten, weitere Einträge können über das Python SDK hinzugefügt werden.",
    button: "Datensatz erstellen",
    fields: "Felder",
    questionsTitle: "Fragen",
    yourQuestions: "Ihre Fragen",
    requiredField: "Pflichtfeld",
    requiredQuestion: "Pflichtfrage",
    select: "Auswählen",
    mapToColumn: "Einer Spalte zuordnen",
    subset: "Teilmenge",
    selectSubset:
      "Sie können einen Datensatz nur aus einer Teilmenge erstellen.",
    preview: "Vorschau",
    importData: "Daten importieren",
    addRecords: "Einträge hinzufügen",
    cantLoadRepository:
      "Datensatz auf Hugging Face nicht gefunden oder verfügbar",
    none: "Keine",
    noWorkspaces:
      "Bitte folgen Sie der <a target='_blank' href='https://docs.argilla.io/latest/how_to_guides/workspace/#create-a-new-workspace'>Anleitung</a>, um einen Workspace zu erstellen",
  },
  config: {
    field: {
      text: "Textfeld",
      chat: "Chatfeld",
      image: "Bildfeld",
      "no mapping": "Keine Zuordnung",
    },
    question: {
      text: "Text",
      rating: "Numerische Bewertung",
      label_selection: "Label",
      ranking: "Ranking",
      multi_label_selection: "Multi-Label",
      span: "Bereichsannotation",
      "no mapping": "Keine Zuordnung",
    },
  },
  persistentStorage: {
    adminOrOwner:
      "Der persistente Speicher ist nicht aktiviert. Alle Daten gehen verloren, wenn dieser Space neu gestartet wird. Gehen Sie zu den Space-Einstellungen, um ihn zu aktivieren.",
    annotator:
      "Der persistente Speicher ist nicht aktiviert. Alle Daten gehen verloren, wenn dieser Space neu gestartet wird.",
  },
  colorSchema: {
    system: "System",
    light: "Licht",
    dark: "Dunkel",
    "high-contrast": "Hoher Kontrast",
  },
  validations: {
    businessLogic: {
      missing_vector: {
        message: "Vektor nicht im ausgewählten Datensatz gefunden",
      },
      update_distribution_with_existing_responses: {
        message:
          "Die Verteilungseinstellungen können für einen Datensatz mit Benutzerantworten nicht geändert werden", //TODO
      },
    },
    http: {
      401: {
        message: "Anmeldedaten konnten nicht überprüft werden",
      },
      404: {
        message: "Die angeforderte Ressource konnte nicht gefunden werden",
      },
      429: {
        message:
          "Bitte warten Sie einige Sekunden, bevor Sie es erneut versuchen",
      },
      500: {
        message:
          "Bitte warten Sie einige Sekunden, bevor Sie es erneut versuchen",
      },
    },
  },
};
