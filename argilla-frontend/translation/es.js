export default {
  multi_label_selection: "Selección de múltiples etiquetas",
  ranking: "Ranking",
  label_selection: "Selección de etiqueta",
  span: "Span",
  text: "Texto",
  rating: "Calificación",
  minimize: "Minimizar",
  select: "Seleccionar",
  search: "Buscar",
  searchPlaceholder: "Introduce una consulta",
  searchDatasets: "Buscar datasets",
  expand: "Expandir",
  copied: "Copiado",
  copyLink: "Copiar enlace",
  copyRecord: "Copiar registro",
  refresh: "Refrescar",
  typeYourText: "Escribe tu texto",
  all: "Todas",
  value: "Valor",
  title: "Título",
  description: "Descripción",
  labels: "Etiquetas",
  order: "Orden",
  owner: "Propietario",
  useMarkdown: "Usar Markdown",
  suggestionFirst: "Mostrar sugerencias primero",
  visibleForAnnotators: "Visible para los anotadores",
  recordInfo: "Información del registro",
  viewMetadata: "Ver metadatos",
  allowExtraMetadata: "Permitir metadatos adicionales",
  extraMetadata: "Metadatos adicionales",
  dimension: "Dimensión",
  visibleLabels: "Etiquetas visibles",
  annotationGuidelines: "Directrices de anotación",
  guidelines: "Directrices",
  taskDistribution: "Distribución de tareas",
  minimumSubmittedResponses: "Respuestas mínimas enviadas",
  taskDistributionTooltip:
    "Una tarea se completa cuando todos los registros tienen el número mínimo de respuestas enviadas",
  noAnnotationGuidelines: "Este dataset no tiene directrices de anotación",
  required: "Requerido",
  optional: "Opcional",
  template: "Plantilla",
  rows: "filas",
  datasetName: "Dataset name",
  noRecordsMessages: {
    datasetEmptyForAnnotator:
      "El dataset está vacío. Pide a un administrador que suba registros y vuelve pronto.",
    datasetEmptyForAdmin:
      "El dataset está vacío. Puedes agregar registros usando el SDK de Python, consulta la <a href='https://docs.argilla.io/latest/how_to_guides/record/'>documentación</a> sobre cómo agregar registros.",
    taskDistributionCompleted: "¡La tarea está completada!",
    noSubmittedRecords: "Aún no has enviado ningún registro",
    noRecordsFound:
      "No tienes registros {status} que coincidan con tu búsqueda",
    noRecords: "No tienes registros {status}",
    noPendingRecordsToAnnotate: "No tienes registros pendientes para anotar",
    noDraftRecordsToReview: "No tienes ningún borrador para revisar",
  },
  breadcrumbs: {
    home: "Inicio",
    datasetSettings: "Configuración del dataset",
    userSettings: "Configuración de usuario",
  },
  datasets: {
    left: "pendiente",
    completed: "Completado",
    pending: "Pendiente",
  },
  recordStatus: {
    pending: "pendiente | pendientes",
    draft: "borrador | borradores",
    discarded: "descartado | descartados",
    submitted: "enviado | enviados",
    validated: "validado | validados",
    completedTooltip:
      "El registro está completo, tiene el número mínimo de respuestas",
  },
  userSettings: {
    title: "Configuración de usuario",
    fields: {
      userName: "Nombre de usuario",
      firstName: "Nombre",
      lastName: "Apellido",
      workspaces: "Espacios de trabajo",
    },
    apiKey: "Clave de API",
    apiKeyDescription:
      "Los tokens de clave API permiten administrar datasets utilizando el SDK de Python",
    theme: "Tema",
    language: "Idioma",
    copyKey: "Copiar clave",
  },
  userAvatarTooltip: {
    settings: "Configuración de usuario",
    docs: "Documentación",
    logout: "Cerrar sesión",
  },
  settings: {
    title: "Configuración del dataset",
    datasetInfo: "Información del dataset",
    seeYourDataset: "Ver tu dataset",
    editFields: "Editar campos",
    editQuestions: "Editar preguntas",
    editMetadata: "Editar metadatos",
    editVectors: "Editar vectores",
    deleteDataset: "Eliminar dataset",
    deleteWarning: "Ten cuidado, esta acción no se puede deshacer",
    deleteConfirmation: "Confirmar eliminación",
    deleteConfirmationMessage:
      "Estás a punto de eliminar: <strong>{datasetName}</strong> del espacio de trabajo <strong>{workspaceName}</strong>. Esta acción no se puede deshacer",
    yesDelete: "Sí, eliminar",
    write: "Escribir",
    preview: "Vista previa",
    uiPreview: "Vista previa de la interfaz de usuario",
  },
  button: {
    ignore_and_continue: "Ignorar y continuar",
    login: "Iniciar sesión",
    "hf-login": "Iniciar sesión con Hugging Face",
    sign_in_with_username: "Iniciar sesión con nombre de usuario",
    cancel: "Cancelar",
    continue: "Continuar",
    delete: "Eliminar",
    tooltip: {
      copyToClipboard: "Copiar al portapapeles",
      copyNameToClipboard: "Copiar nombre del dataset al portapapeles",
      copyLinkToClipboard: "Copiar enlace del dataset al portapapeles",
      goToDatasetSettings: "Ir a la configuración del dataset",
      datasetSettings: "Configuración del dataset",
    },
  },
  to_submit_complete_required:
    "Para enviar, completa las respuestas requeridas",
  some_records_failed_to_annotate: "Algunos registros no se pudieron anotar",
  changes_no_submit: "No has enviado tus cambios",
  bulkAnnotation: {
    recordsSelected:
      "1 registro seleccionado | {count} registros seleccionados",
    recordsViewSettings: "Configuración de vista de registros",
    fixedHeight: "Altura fija",
    defaultHeight: "Altura predeterminada",
    to_annotate_record_bulk_required: "No hay registros seleccionados",
    select_to_annotate: "Seleccionar todo",
    pageSize: "Tamaño de página",
    selectAllResults: "Seleccionar todos los registros coincidentes {total}",
    haveSelectedRecords: "Has seleccionado todos los registros {total}",
    actionConfirmation: "Confirmación de acción en bloque",
    actionConfirmationText:
      "Esta acción afectará a {total} registros, ¿Deseas continuar?",
    allRecordsAnnotated: "{total} registros han sido {action}",
    affectedAll: {
      submitted: "enviados",
      discarded: "descartados",
      draft: "guardados como borrador",
    },
  },
  shortcuts: {
    label: "Atajos",
    pagination: {
      go_to_previous_record: "Anterior (←)",
      go_to_next_record: "Siguiente (→)",
    },
  },
  questions_form: {
    validate: "Validar",
    clear: "Borrar",
    reset: "Reiniciar",
    discard: "Descartar",
    submit: "Enviar",
    draft: "Guardar borrador",
    write: "Escribir",
  },
  sorting: {
    label: "Ordenar",
    addOtherField: "+ Agregar otro campo",
    suggestion: {
      score: "Puntuación de sugerencia",
      value: "Valor de sugerencia",
    },
    response: "Valor de respuesta",
    record: "General",
    metadata: "Metadatos",
  },
  suggestion: {
    agent: "\nagente: {agent}",
    score: "\npuntuación: {score}",
    tooltip: "Esta pregunta contiene una sugerencia {agent} {score}",
    filter: {
      value: "Valores de sugerencia",
      score: "Puntuación",
      agent: "Agente",
    },
    plural: "Sugerencias",
    name: "Sugerencia",
  },
  similarity: {
    "record-number": "Número de registro",
    findSimilar: "Buscar similares",
    similarTo: "Similar a",
    similarityScore: "Puntuación de similitud",
    similarUsing: "Similar usando",
    expand: "Expandir",
    collapse: "Colapsar",
  },
  spanAnnotation: {
    shortcutHelper: "Presiona 'Shift' para seleccionar solo caracteres",
    notSupported: "La anotación de tipo span no es compatible con tu navegador",
  },
  login: {
    title: "Iniciar sesión",
    username: "Nombre de usuario",
    usernameDescription: "Introduce tu nombre de usuario",
    password: "Contraseña",
    show: "Mostrar",
    hide: "Ocultar",
    passwordDescription: "Introduce tu contraseña",
    claim: "Trabaja en equipo con tus datos.</br>Perfecciona tus modelos.",
    hf: {
      title: "Bienvenido a {space}",
      subtitle:
        "Únete a <strong>{user}</strong> para construir mejores datasets para IA",
    },
  },
  of: "de",
  status: "Estado",
  filters: "Filtros",
  filterBy: "Filtrar por...",
  fields: "Campos",
  field: "Campo",
  questions: "Preguntas",
  metadata: "Metadatos",
  vectors: "Vectores",
  dangerZone: "Zona de peligro",
  responses: "Respuestas",
  "reset-all": "Restablecer todo",
  reset: "Reiniciar",
  less: "Menos",
  learnMore: "Aprende más",
  with: "con",
  find: "Encontrar",
  cancel: "Cancelar",
  focus_mode: "Modo individual",
  bulk_mode: "Modo en bloque",
  update: "Actualizar",
  youAreOnlineAgain: "Estás en línea de nuevo",
  youAreOffline: "Estás sin conexión",
  write: "Texto",
  preview: "Vista previa",
  datasetTable: {
    name: "Dataset",
    workspace: "Espacio de trabajo",
    createdAt: "Creado",
    lastActivityAt: "Última actividad",
    progress: "Progreso del equipo",
  },
  metrics: {
    total: "total",
    progress: {
      default: "Progreso",
      my: "Mi progreso",
      team: "Progreso del equipo",
    },
  },
  home: {
    argillaDatasets: "Tus datasets",
    none: "Ninguno",
    importTitle: "Importar un dataset desde Hugging Face Hub",
    importText:
      "Comienza con un conjunto de datos del Hub simplemente pegando el nombre del repositorio",
    importButton: "Importar dataset",
    importFromHub: "Importar dataset desde Hugging Face",
    importFromPython: "Importar desde Python",
    importFromPythonHFWarning:
      "Si estás usando un Espacio privado, consulta la <a target='_blank' href='https://docs.argilla.io/latest/getting_started/how-to-configure-argilla-on-huggingface/#how-to-use-private-spaces'>documentación</a>.",
    exampleDatasetsTitle: "¿No sabes por dónde empezar?",
    exampleDatasetsText: "Explora estos datasets de ejemplo",
    guidesTitle: "¿No conoces Argilla?",
    guidesText: "Echa un vistazo a estas guías:",
    pasteRepoIdPlaceholder:
      "Pega el ID del repositorio, por ejemplo, stanfordnlp/imdb",
    demoLink:
      "Ingresa a esta <a href='https://huggingface.co/spaces/argilla/argilla-template-space' target='_blank'>demo</a> para probar Argilla",
    name: "Nombre del dataset",
    updatedAt: "Actualizado",
    createdAt: "Creado",
  },
  datasetCreation: {
    questions: {
      labelSelection: {
        atLeastTwoOptions: "Se requieren al menos dos opciones",
        optionsWithoutLabel: "No se permiten opciones vacías",
        optionsSeparatedByComma: "Usa comas para separar las etiquetas",
      },
      rating: {
        atLeastTwoOptions: "Se requieren al menos dos opciones",
      },
      span: {
        fieldRelated: "Se requiere un campo de texto",
      },
    },
    atLeastOneQuestion: "Se requiere al menos una pregunta.",
    atLeastOneRequired: "Se requiere al menos una pregunta obligatoria.",
    hasInvalidQuestions: "Algunas preguntas son inválidas",
    createDataset: "Crear dataset en Argilla",
    datasetName: "Nombre del dataset",
    name: "Nombre",
    assignWorkspace: "Asignar espacio de trabajo",
    selectSplit: "Seleccionar división",
    recordWarning:
      "El conjunto de datos creado incluirá las primeras 10K filas y se pueden agregar más registros a través del SDK de Python.",
    button: "Crear dataset",
    fields: "Campos",
    questionsTitle: "Preguntas",
    yourQuestions: "Tus preguntas",
    requiredField: "Campo obligatorio",
    requiredQuestion: "Pregunta obligatoria",
    select: "Seleccionar",
    mapToColumn: "Mapear a una columna",
    applyToaAField: "Anotar span en:",
    subset: "Subconjunto",
    selectSubset: "Puedes crear un dataset con un solo subconjunto.",
    preview: "Vista previa",
    importData: "Importar datos",
    addRecords: "Agregar registros",
    cantLoadRepository:
      "No se pudo encontrar o acceder al dataset en Hugging Face",
    none: "Ninguno",
    noWorkspaces:
      "Por favor, sigue <a target='_blank' href='https://docs.argilla.io/latest/how_to_guides/workspace/#create-a-new-workspace'>esta guía</a> para crear un espacio de trabajo",
  },
  exportToHub: {
    dialogTitle: "Exportar dataset a Hugging Face",
    ownerTooltip:
      "Utiliza un nombre de usuario u organización de Hugging Face válidos",
    tokenTooltip: `Utiliza un token de acceso existente o crear un <a href='https://huggingface.co/settings/tokens' target='_blank'>nuevo token</a> con "permiso de escritura"`,
    validations: {
      orgOrUsernameIsRequired:
        "El nombre de usuario u organización es requerido",
      hfTokenIsRequired: "El token de Hugging Face es requerido",
      hfTokenInvalid: "El token de Hugging Face es inválido",
      datasetNameIsRequired: "El nombre del dataset es requerido",
    },
    exporting: "Exportando al hub de Hugging Face",
    private: "Dataset privado",
    public: "Dataset público",
    exportingWarning: "Esto puede tardar unos segundos",
  },
  config: {
    field: {
      text: "Campo de texto",
      chat: "Campo de chat",
      image: "Campo de imagen",
      "no mapping": "Sin mapeo",
    },
    question: {
      text: "Texto",
      rating: "Calificación",
      label_selection: "Selección de etiqueta",
      ranking: "Ranking",
      multi_label_selection: "Selección de múltiples etiquetas",
      span: "Span",
      "no mapping": "Sin mapeo",
    },
  },
  persistentStorage: {
    adminOrOwner:
      "El almacenamiento persistente no está habilitado. Todos los datos se perderán si este espacio se reinicia. Ve a la configuración del espacio para habilitarlo",
    annotator:
      "El almacenamiento persistente no está habilitado. Todos los datos se perderán si este espacio se reinicia",
  },
  colorSchema: {
    system: "Sistema",
    light: "Claro",
    dark: "Oscuro",
    "high-contrast": "Alto contraste",
  },
  validations: {
    businessLogic: {
      missing_vector: {
        message: "No se encontró el vector para el registro seleccionado",
      },
      update_distribution_with_existing_responses: {
        message:
          "No se puede modificar la configuración de distribución para un dataset que contiene respuestas de usuarios",
      },
    },
    http: {
      401: {
        message: "No se pudieron validar las credenciales",
      },
      404: {
        message: "No se encontró el recurso solicitado",
      },
      429: {
        message: "Espera unos segundos antes de intentarlo de nuevo",
      },
      500: {
        message: "Ocurrió un error, inténtalo de nuevo más tarde",
      },
    },
  },
};
