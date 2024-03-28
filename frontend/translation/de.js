export default {
  multi_label_selection: "Multi-label",
  ranking: "Ranking",
  label_selection: "Label",
  text: "Text",
  rating: "Bewertung",
  minimize: "Minimieren",
  select: "Auswählen",
  search: "Suchen",
  expand: "Erweitern",
  copied: "Kopiert",
  title: "Titel",
  description: "Beschreibung",
  labels: "Labels",
  useMarkdown: "Verwende Markdown",
  visibleForAnnotators: "Sichtbar für Annotatoren",
  allowExtraMetadata: "Erlaube extra Metadata",
  extraMetadata: "Extra Metadata",
  dimension: "Dimension",
  visibleLabels: "Sichtbare labels",
  annotationGuidelines: "Annotationsrichtlinien",
  noAnnotationGuidelines: "Dieser Datensatz hat keine Annotationsrichtlinien",
  breadcrumbs: {
    home: "Start",
    datasetSettings: "einstellungen",
    userSettings: "meine einstellungen",
  },
  userSettings: {
    title: "Meine Einstellungen",
    fields: {
      userName: "Nutzername",
      firstName: "Vorname",
      lastName: "Nachname",
      workspaces: "Arbeitsbereiche",
    },
  },
  settings: {
    title: "Datensatz-Einstellungen",
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
  },
  button: {
    ignore_and_continue: "Ignorieren und fortfahren",
    login: "Anmelden",
    "hf-login": "Mit Hugging Face anmelden",
    sign_in_with_username: "Mit Benutzername anmelden",
    cancel: "Abbrechen",
    continue: "Fortfahren",
  },
  to_submit_complete_required: "Zum Absenden beantworten \nSie benötigte Fragen",
  some_records_failed_to_annotate: "Einige Einträge konnten nicht annotiert werden",
  changes_no_submit: "Sie haben Ihre Änderungen nicht gespeichert",
  bulkAnnotation: {
    recordsSelected: "1 Eintrag ausgewählt | {count} Einträge ausgewählt",
    recordsViewSettings: "Anzahl der Einträge",
    fixedHeight: "Einträge zusammenklappen",
    defaultHeight: "Einträge erweitern ",
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
    discard: "Verwerfen",
    submit: "Absenden",
    draft: "Als Entwurf speichern",
  },
  sorting: {
    addOtherField: "+ Ein weiteres Feld hinzufügen",
    suggestion: {
      score: "Vorschlagsbewertung",
      value: "Vorschlagswert",
    },
    response: "Antwortwert",
    record: "allgemein",
    metadata: "metadaten",
  },
  suggestion: {
    agent: "\nagent: {agent}",
    score: "\nbewertung: {score}",
    tooltip: "Diese Frage enthält einen Vorschlag{agent}{score}",
    filter: {
      value: "Vorschlagswerte",
      score: "Bewertung",
      agent: "Agent",
    },
    plural: "Vorschläge",
    "suggested-rank": `Vorgeschlagener Rang`,
    name: `Vorschlag`,
  },
  similarity: {
    "record-number": "Eintrag-Nummer",
    findSimilar: "Ähnliche finden",
    similarTo: "Ähnlich zu",
    similarityScore: "Ähnlichkeitsbewertung",
    similarUsing: "ähnlich unter Verwendung von",
    expand: "Erweitern",
    collapse: "Zusammenklappen",
  },
  spanAnnotation: {
    shortcutHelper: "Halten Sie 'Shift' gedrückt, um Zeichenebene auszuwählen",
    notSupported: "Bereichsannotation wird von Ihrem Browser nicht unterstützt",
    bulkMode: "Bereichsannotation wird in der Massenansicht nicht unterstützt",
  },
  login: {
    title: "Anmelden",
    claim: "Arbeiten Sie gemeinsam an Daten.</br>Verbessern Sie Ihre Modelle.",
    support:
      "Um Unterstützung von der Community zu erhalten, folgen Sie uns auf <a href='{link}' target='_blank'>Slack</a>",
    quickstart:
      "Sie verwenden die Quickstart-Version von Argilla. Überprüfen Sie <a href='{link}' target='_blank'>diesen Leitfaden</a> um mehr über Nutzung und Konfigurationsoptionen zu erfahren.",
    hf: {
      title: "Willkommen bei {space}",
      subtitle: "Helfe <strong>{user}</strong> um bessere Datensätze für KI zu erstellen",
    },
  },
  status: "Status",
  filters: "Filter",
  filterBy: "Filter nach...",
  fields: "Felder",
  questions: "Fragen",
  metadata: "Metadaten",
  vectors: "Vektoren",
  dangerZone: "Gefahrenzone",
  responses: "Antworten",
  "reset-all": "Alle zurücksetzen",
  reset: "Zurücksetzen",
  less: "Weniger",
  with: "mit",
  find: "Finden",
  cancel: "Abbrechen",
  focus_mode: "Fokusansicht",
  bulk_mode: "Massenansicht",
  update: "Aktualisieren",
  youAreOnlineAgain: "Sie sind wieder online",
  youAreOffline: "Sie sind offline",

  validations: {
    http: {
      401: {
        message: "Anmeldedaten konnten nicht überprüft werden",
      },
      404: {
        message: "Die angeforderte Ressource konnte nicht gefunden werden",
      },
      429: {
        message: "Bitte warten Sie einige Sekunden, bevor Sie es erneut versuchen",
      },
      500: {
        message: "Bitte warten Sie einige Sekunden, bevor Sie es erneut versuchen",
      },
    },
  },
};
