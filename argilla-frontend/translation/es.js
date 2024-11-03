export default {
  multi_label_selection: "Multi-Etiqueta",
  ranking: "Ranking",
  label_selection: "Etiqueta",
  span: "Selección",
  text: "Texto",
  rating: "Calificación",
  minimize: "Minimizar",
  select: "Seleccionar",
  search: "Buscar",
  searchPlaceholder: "Introduce una consulta",
  searchDatasets: "Buscar dataset",
  expand: "Expandir",
  copied: "Copiado",
  copyLink: "Copiar enlace",
  copyRecord: "Copiar registro",
  refresh: "Refrescar",
  typeYourText: "Escriba su texto",
  all: "Todas",
  value: "Valor",
  title: "Título",
  description: "Descripción",
  labels: "Etiquetas",
  order: "Orden",
  useMarkdown: "Usar Markdown",
  suggestionFirst: "Mostrar sugerencias primero",
  visibleForAnnotators: "Visible para los anotadores",
  recordInfo: "Información de registro",
  viewMetadata: "Ver metadatos",
  allowExtraMetadata: "Permitir metadatos adicionales",
  extraMetadata: "Metadatos adicionales",
  dimension: "Dimensión",
  visibleLabels: "Etiquetas visibles",
  annotationGuidelines: "Guía de anotación",
  guidelines: "Guía",
  taskDistribution: "Distribución de la tarea",
  minimumSubmittedResponses: "Respuestas mínimas entregadas",
  taskDistributionTooltip:
    "Una tarea se completa cuando todos los \nregistros tienen el número mínimo \nde respuestas entregadas",
  noAnnotationGuidelines: "Este dataset no tiene guía de anotación",
  required: "Requerido",
  optional: "Opcional",
  template: "Plantilla",
  noRecordsMessages: {
    datasetEmptyForAnnotator:
      "El dataset está vacío. Pide a un administrador que suba registros y vuelve pronto.",
    datasetEmptyForAdmin:
      "El dataset está vacío. Puedes agregar registros usando el SDK de Python, consulta la <a href='https://docs.argilla.io/latest/how_to_guides/record/'>documentación</a> sobre cómo agregar registros.",
    taskDistributionCompleted: "🎉 ¡La tarea está completada!",
    noSubmittedRecords: "Aún no has entregado ningún registro",
    noRecordsFound:
      "No tienes registros {status} que coincidan con tu búsqueda",
    noRecords: "No tienes registros {status}",
    noPendingRecordsToAnnotate: "🎉 No tienes registros pendientes para anotar",
    noDraftRecordsToReview: "No tienes ningún borrador para revisar",
  },
  breadcrumbs: {
    home: "Inicio",
    datasetSettings: "Configuración",
    userSettings: "Mi configuración",
  },
  datasets: {
    left: "pendiente",
    completed: "Completada",
    pending: "Pendiente",
  },
  recordStatus: {
    pending: "pendiente | pendientes",
    draft: "borrador | borradores",
    discarded: "descartado | descartados",
    submitted: "entregado | entregados",
    validated: "validado | validados",
    completedTooltip:
      "El registro está completo, tiene el número \nmínimo de respuestas",
  },
  userSettings: {
    title: "Mi configuración",
    fields: {
      userName: "Usuario",
      firstName: "Nombre",
      lastName: "Apellido",
      workspaces: "Espacios de trabajo",
    },
    apiKey: "Clave de API",
    apiKeyDescription:
      "Los tokens de clave API permiten administrar datasets utilizando el SDK de Python",
    copyKey: "Copiar clave",
  },
  userAvatarTooltip: {
    settings: "Mi configuración",
    docs: "Documentación",
    logout: "Cerrar sesión",
  },
  settings: {
    title: "Configuración del dataset",
    datasetInfo: "Información del dataset",
    seeYourDataset: "Ver el dataset",
    editFields: "Editar campos",
    editQuestions: "Editar preguntas",
    editMetadata: "Editar propiedades de metadatos",
    editVectors: "Editar vectores",
    deleteDataset: "Eliminar el dataset",
    deleteWarning: "Ten cuidado, esta acción no es reversible",
    deleteConfirmation: "Confirma la eliminación",
    deleteConfirmationMessage:
      "Estás a punto de eliminar: <strong> {datasetName} </strong> del espacio de trabajo <strong> {workspaceName} </strong>. Esta acción no puede deshacerse",
    yesDelete: "Sí, eliminar",
    write: "Escribir",
    preview: "Vista previa",
    uiPreview: "Vista previa de la interfaz de usuario",
  },
  button: {
    ignore_and_continue: "Ignorar y continuar",
    login: "Iniciar sesión",
    "hf-login": "Iniciar sesión con Hugging Face",
    "hf-login": "Iniciar sesión con Keycloak",
    sign_in_with_username: "Iniciar sesión con usuario",
    cancel: "Cancelar",
    continue: "Continuar",
    delete: "Eliminar",
    tooltip: {
      copyToClipboard: "Copiar en el portapapeles",
      copyNameToClipboard: "Copiar el nombre del dataset al portapapeles",
      copyLinkToClipboard: "Copiar enlace del dataset al portapapeles",
      goToDatasetSettings: "Configuración del dataset",
      datasetSettings: "Configuración del dataset",
    },
  },
  to_submit_complete_required:
    "Para entregar completa \nlas respuestas requeridas",
  some_records_failed_to_annotate: "Algunos registros no fueron anotados",
  changes_no_submit: "No entregó sus cambios",
  bulkAnnotation: {
    recordsSelected:
      "1 registro seleccionado | {count} registros seleccionados",
    recordsViewSettings: "Tamaño de registro",
    fixedHeight: "Colapsar registros",
    defaultHeight: "Expandir registros",
    to_annotate_record_bulk_required: "No hay registro seleccionado",
    select_to_annotate: "Seleccionar todo",
    pageSize: "Tamaño de página",
    selectAllResults: "Selecciona todos los registros coincidentes {total}",
    haveSelectedRecords: "Has seleccionado todos los registros {total}",
    actionConfirmation: "Confirmación de acción en bloque",
    actionConfirmationText:
      "Esta acción afectará a {total} registros, ¿Quiere continuar?",
    allRecordsAnnotated: "{total} registros han sido {action}",
    affectedAll: {
      submitted: "entregados",
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
    submit: "Entregar",
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
    record: "general",
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
    notSupported: "La anotación de tipo span no es compatible con su navegador",
  },
  login: {
    title: "Iniciar sesión",
    username: "Usuario",
    usernameDescription: "Introduce tu usuario",
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
  filterBy: "Filtrar por ...",
  fields: "Campos",
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
  focus_mode: "Individual",
  bulk_mode: "En bloque",
  update: "Actualizar",
  youAreOnlineAgain: "Estás en línea de nuevo",
  youAreOffline: "Estás fuera de línea",
  write: "Texto",
  preview: "Vista previa",
  datasetTable: {
    name: "Dataset",
    workspace: "Espacio de trabajo",
    createdAt: "Creado",
    lastActivityAt: "Actualizado",
    progress: "Progreso del equipo",
  },
  metrics: {
    total: "total",
    progress: {
      my: "Mi progreso",
      team: "Progreso del equipo",
    },
  },
  home: {
    argillaDatasets: "Datasets de Argilla",
    none: "Sin datasets",
    importTitle: "Importar un dataset desde Hugging Face Hub",
    importText:
      "Comienza con un conjunto de datos del Hub simplemente pegando el nombre del repositorio",
    importButton: "Importar dataset",
    importFromHub: "Importar desde el Hub",
    importFromPython: "Importar desde Python",
    importFromPythonHFWarning:
      "Si estás usando un Espacio privado, consulta la <a target='_blank' href='https://docs.argilla.io/latest/getting_started/how-to-configure-argilla-on-huggingface/#how-to-use-private-spaces'>documentación</a>.",
    exampleDatasetsTitle: "¿No sabes por dónde empezar?",
    exampleDatasetsText: "Explora estos datasets de ejemplo",
    guidesTitle: "¿No conoce Argilla?",
    guidesText: "Echa un vistazo a estas guías:",
    pasteRepoIdPlaceholder: "Pega un repo id",
    demoLink:
      "Entra en esta <a href='https://huggingface.co/spaces/argilla/argilla-template-space' target='_blank'>demo</a> para probar Argilla",
  },
  datasetCreation: {
    questions: {
      labelSelection: {
        atLeastTwoOptions: "Se requieren al menos dos opciones",
        optionsWithoutLabel: "No se permiten opciones vacías",
      },
    },
    atLeastOneQuestion: "Se requiere al menos una pregunta",
    atLeastOneRequired: "Se requiere al menos una pregunta obligatoria",
    hasInvalidQuestions: "Algunas preguntas son inválidas",
    createDataset: "Crea el dataset en Argilla",
    datasetName: "Nombre del dataset",
    name: "Nombre",
    assignWorkspace: "Asignar un espacio de trabajo",
    selectSplit: "Seleccionar una división",
    recordWarning:
      "El conjunto de datos creado incluirá las primeras 10K filas y se pueden registrar más records a través del SDK de Python.",
    button: "Crear el dataset",
    fields: "Campos",
    questionsTitle: "Preguntas",
    yourQuestions: "Tus preguntas",
    requiredField: "Campo obligatorio",
    requiredQuestion: "Pregunta obligatoria",
    select: "Seleccionar",
    mapToColumn: "Mapear a una columna",
    subset: "Subconjunto",
    selectSubset: "Puedes crear un dataset de un solo subconjunto.",
    preview: "Vista previa",
    importData: "Importar datos",
    addRecords: "Agregar records",
    cantLoadRepository: "Dataset no encontrado o disponible en Hugging Face",
    none: "Ninguno",
    noWorkspaces:
      "Por favor, sigue <a target='_blank' href='https://docs.argilla.io/latest/how_to_guides/workspace/#create-a-new-workspace'>esta guía</a> para crear un espacio de trabajo",
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
      label_selection: "Etiqueta",
      ranking: "Ranking",
      multi_label_selection: "Multi-Etiqueta",
      span: "Span",
      "no mapping": "Sin mapeo",
    },
  },
  persistentStorage: {
    adminOrOwner:
      "El almacenamiento persistente no está habilitado. Todos los datos se perderán si este espacio se reinicia. Vaya a la configuración del espacio para habilitarlo",
    annotator:
      "El almacenamiento persistente no está habilitado. Todos los datos se perderán si este espacio se reinicia",
  },
  validations: {
    businessLogic: {
      missing_vector: {
        message: "Vector no encontrado para el registro seleccionado",
      },
      update_distribution_with_existing_responses: {
        message:
          "La configuración de distribución no se puede modificar para un dataset que contiene respuestas de usuarios",
      },
    },
    http: {
      401: {
        message: "No se pudo validar las credenciales",
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
