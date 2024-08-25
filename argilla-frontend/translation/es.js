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
  searchPlaceholder: "Introducir una consulta",
  searchDatasets: "Search DataSets",
  expand: "Expandir",
  copied: "Copiado",
  copyLink: "Enlace de copia",
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
  visibleForAnnotators: "Visible para las anotadoras",
  recordInfo: "Información de registro",
  viewMetadata: "Ver metadatos",
  allowExtraMetadata: "Permitir metadatos adicionales",
  extraMetadata: "Metadatos adicionales",
  dimension: "Dimensión",
  visibleLabels: "Etiquetas visibles",
  annotationGuidelines: "Guía de anotación",
  guidelines: "Guías",
  taskDistribution: "Distribución de tareas",
  minimumSubmittedResponses: "Respuestas mínimas enviadas",
  taskDistributionTooltip:
    "Una tarea se completa cuando todos los \nregistros tienen el número mínimo \nde respuestas enviadas",
  noAnnotationGuidelines: "Este conjunto de datos no tiene pautas de anotación",
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
    pending: "Pendiente",
    draft: "Borrador",
    discarded: "Descartado",
    submitted: "Enviado",
    validated: "Validado",
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
      "Los tokens de clave API le permiten administrar conjuntos de datos utilizando el SDK de Python",
    copyKey: "Copiar clave",
  },
  userAvatarTooltip: {
    settings: "Mi configuración",
    docs: "Ver documentos",
    logout: "Cerrar sesión",
  },
  settings: {
    title: "Configuración del conjunto de datos",
    datasetInfo: "Información del conjunto de datos",
    seeYourDataset: "Vea su conjunto de datos",
    editFields: "Editar campos",
    editQuestions: "Editar preguntas",
    editMetadata: "Editar propiedades de metadatos",
    editVectors: "Editar vectores",
    deleteDataset: "Eliminar el conjunto de datos",
    deleteWarning: "Ten cuidado, esta acción no es reversible",
    deleteConfirmation: "Confirma la eliminación",
    deleteConfirmationMessage:
      "Estás a punto de eliminar: <strong> {datasetName} </strong> del espacio de trabajo <strong> {workspaceName} </strong>. Esta acción no puede deshacerse",
    yesDelete: "Sí, Eliminar",
    write: "Escribir",
    preview: "Vista previa",
    uiPreview: "Vista previa de la interfaz de usuario",
  },
  button: {
    ignore_and_continue: "Ignorar y continuar",
    login: "Iniciar sesión",
    "hf-login": "Iniciar sesión con Hugging Face",
    sign_in_with_username: "Iniciar sesión con usuario",
    cancel: "Cancelar",
    continue: "Continuar",
    delete: "Eliminar",
    tooltip: {
      copyToClipboard: "Copiar en el portapapeles",
      copyNameToClipboard:
        "Copiar el nombre del conjunto de datos al portapapeles",
      copyLinkToClipboard:
        "Copiar enlace del conjunto de datos al portapapeles",
      goToDatasetSettings: "Vaya a la configuración del conjunto de datos",
      datasetSettings: "Configuración del conjunto de datos",
    },
  },
  to_submit_complete_required: "Para enviar respuestas completas",
  some_records_failed_to_annotate: "Algunos registros no lograron anotar",
  changes_no_submit: "No envió sus cambios",
  bulkAnnotation: {
    recordsSelected:
      "1 registro seleccionado | {count} registros seleccionados",
    recordsViewSettings: "Tamaño de registro",
    fixedHeight: "Records de colapso",
    defaultHeight: "Expandir registros",
    to_annotate_record_bulk_required: "No hay registro seleccionado",
    select_to_annotate: "Seleccione todo",
    pageSize: "Tamaño de página",
    selectAllResults: "Seleccione todos los registros coincidentes {Total}",
    haveSelectedRecords: "Has seleccionado todos los registros {Total}",
    actionConfirmation: "Confirmación de acción a granel",
    actionConfirmationText:
      "Esta acción afectará {total} registros, ¿Quiere continuar?",
    allRecordsAnnotated: "Los registros {Total} han sido {Action}",
    affectedAll: {
      submitted: "enviado",
      discarded: "descartado",
      draft: "borrador",
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
    clear: "Claro",
    reset: "Reiniciar",
    discard: "Descartar",
    submit: "Entregar",
    draft: "Guardar como borrador",
    write: "Escribir",
  },
  sorting: {
    addOtherField: "+ Agregar otro campo",
    suggestion: {
      score: "Puntuación de sugerencias",
      value: "Valor de sugerencia",
    },
    response: "Valor de respuesta",
    record: "general",
    metadata: "Metadatos",
  },
  suggestion: {
    agent: "\nagente: {agent}",
    score: "\npuntaje: {score}",
    tooltip: "Esta pregunta contiene una sugerencia {agente} {stork}",
    filter: {
      value: "Valores de sugerencia",
      score: "Puntaje",
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
    notSupported: "La anotación en selección no es compatible con su navegador",
  },
  login: {
    title: "Iniciar sesión",
    username: "Usuario",
    usernameDescription: "Ingrese su usuario",
    password: "Contraseña",
    show: "Mostrar",
    hide: "Ocultar",
    passwordDescription: "Ingrese su contraseña",
    claim: "Trabajen en datos juntos. </br> para mejorar sus modelos.",
    hf: {
      title: "Bienvenido a {Space}",
      subtitle:
        "Únete a <strong>{user}</strong> para construir mejores conjuntos de datos para AI",
    },
  },
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
  learnMore: "Aprenda más",
  with: "con",
  find: "Encontrar",
  cancel: "Cancelar",
  focus_mode: "Foco",
  bulk_mode: "Masivo",
  update: "Actualizar",
  youAreOnlineAgain: "Estás en línea de nuevo",
  youAreOffline: "Estás fuera de línea",
  write: "Escritura",
  preview: "Vista previa",
  datasetTable: {
    name: "Conjunto de datos",
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
          "La configuración de distribución no se puede modificar para un conjunto de datos que contiene respuestas del usuario",
      },
    },
    http: {
      401: {
        message: "No pudo validar las credenciales",
      },
      404: {
        message: "No se encontró el recurso solicitado",
      },
      429: {
        message: "Espere unos segundos antes de intentarlo de nuevo",
      },
      500: {
        message: "Ocurrió un error, inténtelo de nuevo más tarde",
      },
    },
  },
};
