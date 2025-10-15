import { ref, computed, onMounted, watch, onUnmounted } from "vue-demi";
import Konva from "konva";
import { useImageAnnotationSharedState } from "./useImageAnnotationSharedState";
import { initKonvaStage } from "./composables/useKonvaStage";
import { loadImageNode } from "./composables/useImageLoader";
import { useResize } from "./composables/useResize";
import { useKeyboardShortcuts } from "./composables/useKeyboardShortcuts";
import { useContextMenu } from "./composables/useContextMenu";
import { AnnotationRenderer } from "./rendering/AnnotationRenderer";
import { getImageCoordinates, getCanvasCoordinates } from "./utils/coordinates";
import {
  isPointWithinParent as checkPointWithinParent,
} from "./utils/geometry";
import { getAnnotationNodes } from "./utils/konvaShapes";
import { completeHoleCreation } from "./utils/holeCreationUtils";
import { AnnotationToolFactory } from "./tools/AnnotationToolFactory";
import { ToolContext } from "./tools/IAnnotationTool";
import { ToolInteraction, InteractionContext } from "./tools/IToolInteraction";
import { Question } from "~/v1/domain/entities/question/Question";
import { ImageAnnotationQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";
import { ImageAnnotationAnswer } from "~/v1/domain/entities/IAnswer";

/**
 * Simplified mode type - only 3 conceptual states
 * Drawing state is now owned by activeInteraction
 */
type Mode =
  | { kind: "idle" }
  | { kind: "drawing" }
  | { kind: "edit"; annotationIndex: number };

export const useImageAnnotationFieldViewModel = (props: {
  id: string;
  name: string;
  content: string;
  imageAnnotationQuestion: Question;
}) => {
  const { content, imageAnnotationQuestion } = props;
  const answer =
    imageAnnotationQuestion.answer as ImageAnnotationQuestionAnswer;
  const sharedState = useImageAnnotationSharedState(answer);

  // Konva objects (managed by composables)
  let stage: Konva.Stage | null = null;
  let imageLayer: Konva.Layer | null = null;
  let annotationLayer: Konva.Layer | null = null;
  let imageNode: Konva.Image | null = null;
  let originalImageWidth = 0;
  let originalImageHeight = 0;
  let toolFactory: AnnotationToolFactory | null = null;
  let renderer: AnnotationRenderer | null = null;

  const canvasContainer = ref<HTMLDivElement | null>(null);
  const imageLoaded = ref(false);
  const hasError = ref(false);
  const hoveredAnnotation = ref<number | null>(null);
  const draggingPoint = ref<{
    annotationIndex: number;
    pointIndex: number;
    holeIndex: number | null;
  } | null>(null);
  const mode = ref<Mode>({ kind: "idle" });
  const activeInteraction = ref<ToolInteraction | null>(null);

  // Use resize composable to handle canvas resizing
  useResize(
    canvasContainer,
    () => stage,
    () => imageNode,
    () => ({ width: originalImageWidth, height: originalImageHeight }),
    () => annotationLayer,
    {
      debounceMs: 150,
      onResize: () => {
        renderAnnotations();
        if (editMode.value.active && editMode.value.annotationIndex !== null) {
          renderAnchorPoints(editMode.value.annotationIndex);
        }
      },
    }
  );

  const editMode = computed(() => ({
    active: sharedState.editModeActive.value,
    annotationIndex: sharedState.currentAnnotationIndex.value,
  }));

  const selectedTool = computed(() => sharedState.selectedTool.value);

  const annotations = computed(() => answer.values);

  const selectedLabel = computed(() => {
    return answer.options.find((opt) => opt.isSelected);
  });

  const getAnnotationColor = (labelValue: string) =>
    answer.getAnnotationColor(labelValue);

  // Removed: createShape() - now in AnnotationRenderer

  // Removed: highlightAnnotationUtil() - now in AnnotationRenderer

  /**
   * Create base context with shared properties
   */
  const getBaseContext = () => ({
    annotationLayer,
    imageLayer,
    imageNode,
    getAnnotationColor,
    getImageCoordinates: (points: number[][], _imageNode: Konva.Image | null) =>
      getImageCoordinates(points, imageNode),
    getCanvasCoordinates: (
      points: number[][],
      _imageNode: Konva.Image | null
    ) => getCanvasCoordinates(points, imageNode),
    updateAnswer,
    renderAnnotations,
  });

  const getToolContext = (): ToolContext => ({
    ...getBaseContext(),
    renderAnchorPoints,
    getToolForShape: (shapeType: string) =>
      toolFactory?.getToolForShape(shapeType) || null,
  });

  const initializeToolFactory = () => {
    toolFactory = new AnnotationToolFactory(getToolContext());
  };

  const initializeRenderer = () => {
    renderer = new AnnotationRenderer({
      annotationLayer,
      imageLayer,
      imageNode,
      toolFactory,
      getAnnotationColor,
      onHoverAnnotation: hoverAnnotation,
      onUnhoverAnnotation: unhoverAnnotation,
    });
  };

  /**
   * Create InteractionContext for tool interactions
   */
  const getInteractionContext = (): InteractionContext => getBaseContext();

  /**
   * Handle interaction result from event handlers
   */
  const handleInteractionResult = (result: {
    shouldComplete?: boolean;
    shouldCancel?: boolean;
    shouldContinue?: boolean;
  }) => {
    if (result.shouldComplete) {
      completeInteraction();
    } else if (result.shouldCancel) {
      cancelInteraction();
    }
    // shouldContinue or undefined - interaction continues
  };

  /**
   * Start a new drawing interaction
   */
  const startDrawingInteraction = (pos: { x: number; y: number }) => {
    const tool = toolFactory?.getTool(selectedTool.value);
    if (!tool) return;

    // Determine if we're in hole drawing mode
    const isHole = sharedState.holeDrawingMode.value.active;
    const parentIndex =
      sharedState.holeDrawingMode.value.parentIndex ?? undefined;

    if (isHole && parentIndex !== undefined) {
      // Drawing a hole - check if point is within parent
      if (!isPointWithinParent(pos, parentIndex)) return;

      const color = getAnnotationColor(annotations.value[parentIndex].label);
      activeInteraction.value = tool.createInteraction(
        getInteractionContext(),
        pos,
        color,
        true,
        parentIndex
      );
    } else {
      // Drawing a normal annotation
      if (!selectedLabel.value) {
        alert("Please select a label first");
        return;
      }

      const color = selectedLabel.value.color || "#cccccc";
      activeInteraction.value = tool.createInteraction(
        getInteractionContext(),
        pos,
        color,
        false,
        undefined,
        selectedLabel.value
      );
    }

    mode.value = { kind: "drawing" };
  };

  const isPointWithinParent = (
    point: { x: number; y: number },
    parentIndex: number
  ): boolean => {
    const parent = annotations.value[parentIndex];
    if (!parent) return false;

    const canvasPoints = getCanvasCoordinates(parent.points, imageNode);
    return checkPointWithinParent(point, canvasPoints);
  };

  /**
   * Complete the current interaction and create annotation or hole
   */
  const completeInteraction = () => {
    if (!activeInteraction.value) return;

    const annotation = activeInteraction.value.complete();

    if (annotation) {
      // Normal annotation creation
      answer.values.push(annotation);
      updateAnswer();
    } else if (
      activeInteraction.value.isHole &&
      activeInteraction.value.parentIndex !== undefined
    ) {
      // Hole creation
      const parentIndex = activeInteraction.value.parentIndex;
      const parent = annotations.value[parentIndex];

      // Use utility to complete hole creation
      const success = completeHoleCreation(
        activeInteraction.value,
        parent,
        getImageCoordinates,
        imageNode
      );

      if (!success) {
        // Failed to create hole - cleanup and exit
        activeInteraction.value.cleanup();
        activeInteraction.value = null;
        mode.value = { kind: "idle" };
        return;
      }

      updateAnswer();

      // Stay in hole drawing mode for adding more holes
      highlightParentForHoleDrawing(parentIndex);
    }

    activeInteraction.value.cleanup();
    activeInteraction.value = null;
    mode.value = { kind: "idle" };
    renderAnnotations();
  };

  /**
   * Cancel the current interaction
   */
  const cancelInteraction = () => {
    if (!activeInteraction.value) return;

    activeInteraction.value.cancel();
    activeInteraction.value = null;
    mode.value = { kind: "idle" };
  };

  const highlightAnnotation = (index: number, highlight: boolean) => {
    if (!renderer) return;
    const isEditing =
      editMode.value.active && editMode.value.annotationIndex === index;
    const annotation = annotations.value[index];
    const color = getAnnotationColor(annotation.label);

    renderer.highlightAnnotation(index, highlight, isEditing, color);
  };

  const hoverAnnotation = (index: number) => {
    hoveredAnnotation.value = index;
    if (!editMode.value.active) {
      highlightAnnotation(index, true);
    }
  };

  const unhoverAnnotation = () => {
    if (hoveredAnnotation.value !== null && !editMode.value.active) {
      highlightAnnotation(hoveredAnnotation.value, false);
    }
    hoveredAnnotation.value = null;
  };

  // Removed: showContextMenu() - now contextMenu.show()
  // Removed: hideContextMenu() - now contextMenu.hide()

  const enterEditMode = (annotationIndex: number) => {
    // Cancel any ongoing drawing
    if (activeInteraction.value) {
      cancelInteraction();
    }

    // Exit hole drawing mode if active
    if (sharedState.holeDrawingMode.value.active) {
      const parentIndex = sharedState.holeDrawingMode.value.parentIndex;

      // Restore all annotations
      restoreAllAnnotations();

      // Remove parent highlight
      if (parentIndex !== null) {
        highlightAnnotation(parentIndex, false);
      }

      // Clear hole drawing mode
      sharedState.holeDrawingMode.value = {
        active: false,
        parentIndex: null,
      };
    }

    // Update mode state
    mode.value = { kind: "edit", annotationIndex };

    // Update sharedState (editMode computed will reflect this)
    sharedState.editModeActive.value = true;
    sharedState.currentAnnotationIndex.value = annotationIndex;

    // Broadcast edit mode state to question component
    (answer as any).editModeState = true;

    // Signal to question component to select the annotation's label
    const annotation = annotations.value[annotationIndex];
    if (annotation && annotation.label) {
      sharedState.selectLabelData.value = {
        labelValue: annotation.label,
      };
      sharedState.selectLabelTrigger.value++;
    }

    // Move edited shape to top of z-order (so it receives events first)
    const shapeNode = annotationLayer?.findOne(
      `#annotation-${annotationIndex}`
    );
    const groupNode = annotationLayer?.findOne(
      `.annotation-group#annotation-${annotationIndex}`
    );
    if (shapeNode) {
      shapeNode.moveToTop();
    } else if (groupNode) {
      groupNode.moveToTop();
    }

    // Show anchor points for the selected annotation
    renderAnchorPoints(annotationIndex);

    // Highlight the annotation
    highlightAnnotation(annotationIndex, true);

    // Fade other annotations
    fadeNonEditedAnnotations(annotationIndex);

    contextMenu.hide();

    annotationLayer?.batchDraw();
  };

  const exitEditMode = () => {
    if (editMode.value.annotationIndex !== null) {
      highlightAnnotation(editMode.value.annotationIndex, false);
    }

    removeAnchorPoints();

    // Restore original z-order by re-rendering all annotations
    // This ensures consistent ordering based on array index
    renderAnnotations();

    restoreAllAnnotations();

    // Update mode state
    mode.value = { kind: "idle" };

    // Update sharedState (editMode computed will reflect this)
    sharedState.editModeActive.value = false;
    sharedState.currentAnnotationIndex.value = null;

    // Broadcast edit mode state to question component
    (answer as any).editModeState = false;

    annotationLayer?.batchDraw();
  };

  const editNextAnnotation = () => {
    if (!editMode.value.active || editMode.value.annotationIndex === null)
      return;

    const currentIndex = editMode.value.annotationIndex;
    const nextIndex = (currentIndex + 1) % annotations.value.length;

    enterEditMode(nextIndex);
  };

  const editPreviousAnnotation = () => {
    if (!editMode.value.active || editMode.value.annotationIndex === null)
      return;

    const currentIndex = editMode.value.annotationIndex;
    const prevIndex =
      currentIndex === 0 ? annotations.value.length - 1 : currentIndex - 1;

    enterEditMode(prevIndex);
  };

  /**
   * Delete a shape (annotation) from the canvas and data.
   * Called from: question list, context menu, keyboard shortcuts.
   */
  const deleteShape = (index: number) => {
    // If we're in edit mode and deleting the shape being edited, exit edit mode first
    // This ensures anchor points and edge handles are properly removed
    if (editMode.value.active && editMode.value.annotationIndex === index) {
      exitEditMode();
    }

    answer.deleteAnnotation(index);

    // Update answer - this triggers the watch on answer.values.length which re-renders the canvas
    updateAnswer();
  };

  // Removed: handleContextMenuDelete() - now in useContextMenuHandlers composable
  // Removed: handleContextMenuEdit() - now in useContextMenuHandlers composable
  // Removed: handleContextMenuAddHole() - now in useContextMenuHandlers composable
  // Removed: handleContextMenuDeleteHole() - now in useContextMenuHandlers composable

  const enterHoleDrawingMode = (parentIndex: number) => {
    // Cancel any ongoing drawing
    if (activeInteraction.value) {
      cancelInteraction();
    }

    // Exit edit mode if active
    if (editMode.value.active) {
      exitEditMode();
    }

    // Check if parent already has 10 holes
    const parent = annotations.value[parentIndex];
    if (parent.holes && parent.holes.length >= 10) {
      alert("Maximum 10 holes per shape reached");
      return;
    }

    // Set hole drawing mode
    sharedState.holeDrawingMode.value = {
      active: true,
      parentIndex,
    };

    // Highlight the parent shape
    highlightParentForHoleDrawing(parentIndex);

    // Fade other annotations
    fadeNonEditedAnnotations(parentIndex);
  };

  const exitHoleDrawingMode = () => {
    if (!sharedState.holeDrawingMode.value.active) return;

    // Cancel any ongoing drawing
    if (activeInteraction.value) {
      cancelInteraction();
    }

    const parentIndex = sharedState.holeDrawingMode.value.parentIndex;

    // Restore all annotations
    restoreAllAnnotations();

    // Remove parent highlight
    if (parentIndex !== null) {
      highlightAnnotation(parentIndex, false);
    }

    // Clear hole drawing mode
    sharedState.holeDrawingMode.value = {
      active: false,
      parentIndex: null,
    };
  };

  const highlightParentForHoleDrawing = (parentIndex: number) => {
    if (!renderer) return;
    const annotation = annotations.value[parentIndex];
    renderer.highlightParentForHoleDrawing(parentIndex, annotation);
  };

  const fadeNonEditedAnnotations = (editingIndex: number) => {
    if (!renderer) return;
    renderer.fadeNonEditedAnnotations(editingIndex, annotations.value);
  };

  const restoreAllAnnotations = () => {
    if (!renderer) return;
    renderer.restoreAllAnnotations(annotations.value);
  };

  // Removed: renderParentBoundaryGuide() - now in AnnotationRenderer

  const renderAnchorPoints = (annotationIndex: number) => {
    if (!renderer) return;

    const annotation = annotations.value[annotationIndex];
    if (!annotation) return;

    const color = getAnnotationColor(annotation.label);

    const anchorConfig = {
      annotationIndex,
      pointIndex: 0, // Will be overridden by tool
      holeIndex: null,
      onDragStart: (annIdx: number, ptIdx: number, holeIdx: number | null) => {
        draggingPoint.value = {
          annotationIndex: annIdx,
          pointIndex: ptIdx,
          holeIndex: holeIdx,
        };
      },
      onDragMove: (
        annIdx: number,
        ptIdx: number,
        pos: { x: number; y: number },
        holeIdx: number | null
      ) => {
        // Constrain point if editing a hole
        let constrainedPos = pos;
        if (holeIdx !== null && toolFactory) {
          // Get the tool for the hole being dragged (not the parent)
          const holeShape = annotation.holes?.[holeIdx];
          if (holeShape) {
            const holeTool = toolFactory.getToolForShape(holeShape.shape_type);
            if (holeTool) {
              constrainedPos = holeTool.constrainPointToParentShape(
                annotation,
                pos,
                holeIdx
              );
            }
          }
        }
        updateAnnotationFromDrag(annIdx, ptIdx, constrainedPos, holeIdx);
      },
      onDragEnd: (annIdx: number) => {
        finalizeAnnotationEdit(annIdx);
        draggingPoint.value = null;
      },
      attachContextMenuHandler: contextMenu.attachContextMenuHandler,
    };

    renderer.renderAnchorPoints(annotation, annotationIndex, color, anchorConfig);
  };

  const removeAnchorPoints = () => {
    if (!renderer) return;
    renderer.removeAnchorPoints();
  };

  const updateAnnotationFromDrag = (
    annotationIndex: number,
    pointIndex: number,
    newPos: { x: number; y: number },
    holeIndex: number | null
  ) => {
    const annotation = annotations.value[annotationIndex];
    if (!annotation || !toolFactory) return;

    // Determine which shape is being dragged (hole or parent)
    const targetShape =
      holeIndex !== null ? annotation.holes?.[holeIndex] : annotation;
    if (!targetShape) return;

    // Get the tool for the actual shape being dragged
    const tool = toolFactory.getToolForShape(targetShape.shape_type);
    if (!tool) return;

    tool.updateAnnotationFromDrag(annotation, pointIndex, newPos, holeIndex);
    updateAnnotationShape(annotationIndex);
  };

  const updateAnnotationShape = (annotationIndex: number) => {
    const annotation = annotations.value[annotationIndex];
    if (!annotation || !toolFactory) return;

    const tool = toolFactory.getToolForShape(annotation.shape_type);
    if (!tool) return;

    tool.updateAnnotationShape(annotation, annotationIndex);
  };

  const finalizeAnnotationEdit = (annotationIndex: number) => {
    // Save the changes
    updateAnswer();

    // Re-render anchor points at new positions
    renderAnchorPoints(annotationIndex);
  };

  const initCanvas = () => {
    if (!canvasContainer.value) return;

    // Use composable to initialize stage and layers
    const stageRefs = initKonvaStage(
      canvasContainer.value,
      handleMouseDown,
      handleMouseMove,
      handleMouseUp
    );

    stage = stageRefs.stage;
    imageLayer = stageRefs.imageLayer;
    annotationLayer = stageRefs.annotationLayer;

    // Initialize tool factory after layers are created
    initializeToolFactory();

    // Use composable to load image
    loadImageNode(content, stage, imageLayer)
      .then(({ imageNode: node, originalWidth, originalHeight }) => {
        imageNode = node;
        originalImageWidth = originalWidth;
        originalImageHeight = originalHeight;
        
        // Initialize renderer AFTER imageNode is available
        // This ensures coordinate transformations work correctly
        initializeRenderer();
        
        imageLoaded.value = true;
        renderAnnotations();
      })
      .catch(() => {
        hasError.value = true;
      });

    // Keyboard listener now handled by useKeyboardShortcuts composable
  };

  // Removed: loadImage() - now handled by loadImageNode composable
  // Removed: setupEventHandlers() - now handled by initKonvaStage composable

  // Handle mouse events
  const handleMouseDown = () => {
    const pos = stage?.getPointerPosition();
    if (!pos) return;

    if (activeInteraction.value) {
      // Delegate to active interaction
      const result = activeInteraction.value.onPointerDown(pos);
      handleInteractionResult(result);
    } else if (mode.value.kind === "idle") {
      // Start new interaction
      startDrawingInteraction(pos);
    }
  };

  const handleMouseMove = () => {
    const pos = stage?.getPointerPosition();
    if (!pos || !activeInteraction.value) return;

    activeInteraction.value.onPointerMove(pos);
  };

  const handleMouseUp = () => {
    const pos = stage?.getPointerPosition();
    if (!pos || !activeInteraction.value) return;

    const result = activeInteraction.value.onPointerUp(pos);
    handleInteractionResult(result);
  };

  // Removed: handleKeyDown() - now handled by useKeyboardShortcuts composable
  // Removed: attachContextMenuHandler() - now handled by useContextMenuHandlers composable
  // Removed: attachHoverHandlers() - now in AnnotationRenderer
  // Removed: renderAnnotationWithHoles() - now in AnnotationRenderer
  // Removed: renderSimpleAnnotation() - now in AnnotationRenderer

  const renderAnnotations = () => {
    if (!renderer) return;
    renderer.renderAnnotations(
      annotations.value,
      contextMenu.attachContextMenuHandler
    );
  };

  const updateAnswer = () => {
    imageAnnotationQuestion.answer.response({
      value: answer.valuesAnswered,
    });
  };

  // Removed: resizeCanvas() - now handled by useResize composable

  // Initialize composables after all functions are declared
  // Context menu (consolidated state + handlers)
  const contextMenu = useContextMenu({
    onDelete: deleteShape,
    onEdit: enterEditMode,
    onAddHole: enterHoleDrawingMode,
    onDeleteHole: (annotationIndex, holeIndex) => {
      const annotation = annotations.value[annotationIndex];
      if (annotation && annotation.holes && annotation.holes[holeIndex]) {
        annotation.holes.splice(holeIndex, 1);
        if (annotation.holes.length === 0) {
          delete annotation.holes;
        }
        updateAnswer();
        renderAnnotations();
        if (
          editMode.value.active &&
          editMode.value.annotationIndex === annotationIndex
        ) {
          renderAnchorPoints(annotationIndex);
        }
      }
    },
  });

  // Keyboard shortcuts
  useKeyboardShortcuts(
    {
      mode,
      activeInteraction,
      holeDrawingModeActive: computed(() => sharedState.holeDrawingMode.value.active),
      annotationCount: computed(() => annotations.value.length),
    },
    {
      onExitEditMode: exitEditMode,
      onNextAnnotation: editNextAnnotation,
      onPreviousAnnotation: editPreviousAnnotation,
      onDeleteInEditMode: () => {
        if (mode.value.kind === "edit" && mode.value.annotationIndex !== null) {
          const indexToDelete = mode.value.annotationIndex;
          if (annotations.value.length > 1) {
            editNextAnnotation();
          } else {
            exitEditMode();
          }
          deleteShape(indexToDelete);
        }
      },
      onExitHoleDrawingMode: exitHoleDrawingMode,
      onInteractionKeyDown: (e) => {
        if (activeInteraction.value) {
          const result = activeInteraction.value.onKeyDown(e);
          handleInteractionResult(result);
        }
      },
    }
  );

  // Watch for changes in annotations from the question component
  watch(
    () => answer.values.length,
    () => {
      renderAnnotations();
    }
  );

  // Watch for cancel polygon signal from question component
  watch(sharedState.cancelPolygonTrigger, () => {
    if (activeInteraction.value) {
      cancelInteraction();
    }
  });

  // Watch for enter edit mode signal from question component
  watch(sharedState.enterEditModeTrigger, () => {
    const editModeData = sharedState.enterEditModeData.value;
    if (
      editModeData &&
      editModeData.index !== null &&
      editModeData.index !== undefined
    ) {
      enterEditMode(editModeData.index);
    }
  });

  // Watch for exit edit mode signal from question component
  watch(sharedState.exitEditModeTrigger, () => {
    if (editMode.value.active) {
      exitEditMode();
    }
  });

  // Watch for delete shape signal from question component
  watch(sharedState.deleteShapeTrigger, () => {
    const deleteData = sharedState.deleteShapeData.value;
    if (
      deleteData &&
      deleteData.index !== null &&
      deleteData.index !== undefined
    ) {
      deleteShape(deleteData.index);
    }
  });

  // Watch for delete hole signal from question component
  watch(sharedState.deleteHoleTrigger, () => {
    const deleteData = sharedState.deleteHoleData.value;
    if (
      deleteData &&
      deleteData.annotationIndex !== null &&
      deleteData.holeIndex !== null
    ) {
      const annotation = annotations.value[deleteData.annotationIndex];
      if (
        annotation &&
        annotation.holes &&
        annotation.holes[deleteData.holeIndex]
      ) {
        // Remove the hole from the array
        annotation.holes.splice(deleteData.holeIndex, 1);

        // If no holes left, remove the holes array
        if (annotation.holes.length === 0) {
          delete annotation.holes;
        }

        // Update the answer
        updateAnswer();

        // Re-render the canvas
        renderAnnotations();

        // If in edit mode for this annotation, re-render anchor points
        if (
          editMode.value.active &&
          editMode.value.annotationIndex === deleteData.annotationIndex
        ) {
          renderAnchorPoints(deleteData.annotationIndex);
        }
      }
    }
  });

  // Watch for label reassignment in edit mode
  watch(sharedState.reassignLabelTrigger, () => {
    const reassignData = sharedState.reassignLabelData.value;
    if (
      reassignData &&
      editMode.value.active &&
      editMode.value.annotationIndex !== null
    ) {
      const annotationIndex = editMode.value.annotationIndex;
      const annotation = annotations.value[annotationIndex];

      if (annotation) {
        // Update the annotation's label
        annotation.label = reassignData.labelValue;

        // Re-render the annotation with new color
        renderAnnotations();

        // Re-render anchor points if in edit mode
        renderAnchorPoints(annotationIndex);

        // Update the answer
        updateAnswer();
      }
    }
  });

  // Watch for hole drawing mode signal from question component
  watch(sharedState.holeDrawingMode, (holeMode, oldHoleMode) => {
    // Enter hole drawing mode when activated from question component
    if (holeMode.active && holeMode.parentIndex !== null) {
      // Check if this is a new activation (not already in hole mode for this parent)
      const isNewActivation =
        !oldHoleMode?.active ||
        oldHoleMode.parentIndex !== holeMode.parentIndex;
      if (isNewActivation) {
        enterHoleDrawingMode(holeMode.parentIndex);
      }
    }
  });

  onMounted(() => {
    initCanvas();

    // Close context menu on click outside
    document.addEventListener("click", contextMenu.hide);
  });

  onUnmounted(() => {
    document.removeEventListener("click", contextMenu.hide);
  });

  stage?.destroy();

  return {
    canvasContainer,
    imageLoaded,
    hasError,
    contextMenu: contextMenu.state,
    editMode,
    holeDrawingMode: computed(() => sharedState.holeDrawingMode.value),
    deleteShape,
    handleContextMenuDelete: contextMenu.handleDelete,
    handleContextMenuEdit: contextMenu.handleEdit,
    handleContextMenuAddHole: contextMenu.handleAddHole,
    handleContextMenuDeleteHole: contextMenu.handleDeleteHole,
    enterEditMode,
    exitEditMode,
    exitHoleDrawingMode,
    editNextAnnotation,
    editPreviousAnnotation,
  };
};
