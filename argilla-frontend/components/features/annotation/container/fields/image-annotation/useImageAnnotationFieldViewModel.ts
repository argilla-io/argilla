import { ref, computed, onMounted, watch, onUnmounted, type Ref } from "vue-demi";
import Konva from "konva";
import { Question } from "~/v1/domain/entities/question/Question";
import { ImageAnnotationQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";
import { ImageAnnotationAnswer } from "~/v1/domain/entities/IAnswer";

type Tool = "select" | "rectangle" | "polygon";

// Mode state machine - replaces isDrawing, isDrawingPolygon, and related state
type Mode =
  | { kind: "idle" }
  | { kind: "draw-rect"; start: { x: number; y: number }; color: string }
  | { kind: "draw-poly"; color: string; points: number[]; circles: Konva.Circle[]; previewLine: Konva.Line | null }
  | { kind: "edit"; index: number }
  | { kind: "draw-hole-poly"; parentIndex: number; color: string; points: number[]; circles: Konva.Circle[]; previewLine: Konva.Line | null }
  | { kind: "draw-hole-rect"; parentIndex: number; start: { x: number; y: number }; color: string };

export const useImageAnnotationFieldViewModel = (props: {
  id: string;
  name: string;
  content: string;
  imageAnnotationQuestion: Question;
}) => {
  const { content, imageAnnotationQuestion } = props;
  
  const canvasContainer = ref<HTMLDivElement | null>(null);
  const imageLoaded = ref(false);
  const hasError = ref(false);
  const hoveredAnnotation = ref<number | null>(null);
  const contextMenu = ref<{ visible: boolean; x: number; y: number; annotationIndex: number | null; holeIndex: number | null }>({
    visible: false,
    x: 0,
    y: 0,
    annotationIndex: null,
    holeIndex: null,
  });
  const draggingPoint = ref<{ annotationIndex: number; pointIndex: number; holeIndex: number | null } | null>(null);
  
  // Mode state machine - single source of truth for interaction state
  const mode = ref<Mode>({ kind: "idle" });
  
  // Computed helpers for checking mode state
  const isIdle = computed(() => mode.value.kind === "idle");
  const isDrawingRect = computed(() => mode.value.kind === "draw-rect" || mode.value.kind === "draw-hole-rect");
  const isDrawingPoly = computed(() => mode.value.kind === "draw-poly" || mode.value.kind === "draw-hole-poly");
  const isInEditMode = computed(() => mode.value.kind === "edit");
  
  // Use sharedState directly for edit mode - no local state
  const editMode = computed(() => ({
    active: sharedState.editModeActive.value,
    annotationIndex: sharedState.currentAnnotationIndex.value,
  }));

  let stage: Konva.Stage | null = null;
  let imageLayer: Konva.Layer | null = null;
  let layer: Konva.Layer | null = null;
  let imageNode: Konva.Image | null = null;
  let drawingShape: Konva.Rect | Konva.Line | null = null;
  let resizeTimeout: NodeJS.Timeout | null = null;
  let originalImageWidth = 0;
  let originalImageHeight = 0;
  let resizeObserver: ResizeObserver | null = null;
  const CLOSE_THRESHOLD = 10;

  const answer = imageAnnotationQuestion.answer as ImageAnnotationQuestionAnswer;

  const annotations = computed(() => answer.values);

  type SharedState = {
    editModeActive: Ref<boolean>;
    currentAnnotationIndex: Ref<number | null>;
    reassignLabel: Ref<{ labelValue: string; timestamp: number } | null>;
    deleteShapeSignal: Ref<{ index: number; timestamp: number } | null>;
    deleteHoleSignal: Ref<{ annotationIndex: number; holeIndex: number; timestamp: number } | null>;
    enterEditModeSignal: Ref<{ index: number; timestamp: number } | null>;
    exitEditModeSignal: Ref<boolean>;
    selectLabelSignal: Ref<{ labelValue: string; timestamp: number } | null>;
    holeDrawingMode: Ref<{ active: boolean; parentIndex: number | null }>;
  };

  const ensureSharedState = (target: ImageAnnotationQuestionAnswer): SharedState => {
    const answerTarget = target as any;
    if (!answerTarget.__imageAnnotationSync) {
      const syncState: SharedState = {
        editModeActive: ref(false),
        currentAnnotationIndex: ref<number | null>(null),
        reassignLabel: ref(null),
        deleteShapeSignal: ref(null),
        deleteHoleSignal: ref(null),
        enterEditModeSignal: ref(null),
        exitEditModeSignal: ref(false),
        selectLabelSignal: ref(null),
        holeDrawingMode: ref({ active: false, parentIndex: null }),
      };
      answerTarget.__imageAnnotationSync = syncState;
    }
    return answerTarget.__imageAnnotationSync as SharedState;
  };

  const sharedState = ensureSharedState(answer);

  const selectedLabel = computed(() => {
    return answer.options.find((opt) => opt.isSelected);
  });

  // Track the selected tool reactively
  const selectedTool = ref<string>((answer as any).selectedTool || "rectangle");

  // Poll for tool changes from the question component (since answer.selectedTool is not reactive)
  const toolPollInterval = setInterval(() => {
    const answerTool = (answer as any).selectedTool;
    if (answerTool && answerTool !== selectedTool.value) {
      selectedTool.value = answerTool;
    }
  }, 100); // Check every 100ms

  const getAnnotationColor = (labelValue: string) => {
    const option = answer.options.find((opt) => opt.value === labelValue);
    return option?.color || "#cccccc";
  };

  type AnnotationNodes = {
    element: Konva.Group | Konva.Shape | null;
    parentShape: Konva.Shape | null;
    holeShapes: Konva.Shape[];
  };

  const getAnnotationNodes = (index: number): AnnotationNodes => {
    const element = layer?.findOne(`#annotation-${index}`) as Konva.Group | Konva.Shape | null;
    if (!element) return { element: null, parentShape: null, holeShapes: [] };

    if (element instanceof Konva.Group) {
      const parentShape = element.findOne('.annotation-shape') as Konva.Shape | null;
      const holeShapes = element.find('.annotation-hole') as Konva.Shape[];
      return { element, parentShape, holeShapes };
    }
    return { element, parentShape: element as Konva.Shape, holeShapes: [] };
  };

  const highlightAnnotation = (index: number, highlight: boolean) => {
    const { element, parentShape, holeShapes } = getAnnotationNodes(index);
    if (!element || !parentShape) return;

    const isEditing = editMode.value.active && editMode.value.annotationIndex === index;
    const annotation = annotations.value[index];
    const color = getAnnotationColor(annotation.label);

    if (isEditing) {
      // Editing mode: thicker stroke + glow effect + semi-transparent
      (parentShape as any).strokeWidth(4);
      (parentShape as any).shadowColor(color);
      (parentShape as any).shadowBlur(8);
      (parentShape as any).shadowOpacity(0.8);
      (parentShape as any).opacity(0.5);
    } else {
      // Normal hover or no hover
      (parentShape as any).strokeWidth(highlight ? 4 : 2);
      (parentShape as any).shadowBlur(0);
      (parentShape as any).opacity(0.3);
    }

    // Update hole strokes as well
    holeShapes.forEach((holeShape) => {
      (holeShape as any).strokeWidth(isEditing ? 4 : highlight ? 4 : 2);
    });
    
    const stage = element.getStage();
    if (stage && !editMode.value.active) {
      stage.container().style.cursor = highlight ? 'pointer' : 'default';
    }
    layer?.batchDraw();
    imageLayer?.batchDraw();
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

  const showContextMenu = (index: number, x: number, y: number, holeIndex: number | null = null) => {
    contextMenu.value = {
      visible: true,
      x,
      y,
      annotationIndex: index,
      holeIndex,
    };
  };

  const enterEditMode = (annotationIndex: number) => {
    // Cancel any ongoing drawing using mode state
    if (mode.value.kind === "draw-poly" || mode.value.kind === "draw-hole-poly") {
      cancelPolygon();
    }

    // Update mode state
    mode.value = { kind: "edit", index: annotationIndex };

    // Update sharedState (editMode computed will reflect this)
    sharedState.editModeActive.value = true;
    sharedState.currentAnnotationIndex.value = annotationIndex;

    // Broadcast edit mode state to question component
    (answer as any).editModeState = true;
    
    // Signal to question component to select the annotation's label
    const annotation = annotations.value[annotationIndex];
    if (annotation && annotation.label) {
      sharedState.selectLabelSignal.value = { 
        labelValue: annotation.label, 
        timestamp: Date.now() 
      };
      
      // Reset signal after a tick
      setTimeout(() => {
        sharedState.selectLabelSignal.value = null;
      }, 100);
    }
    
    // Show anchor points for the selected annotation
    renderAnchorPoints(annotationIndex);
    
    // Highlight the annotation
    highlightAnnotation(annotationIndex, true);
    
    // Fade other annotations
    fadeNonEditedAnnotations(annotationIndex);
    
    hideContextMenu();
  };

  const exitEditMode = () => {
    if (editMode.value.annotationIndex !== null) {
      highlightAnnotation(editMode.value.annotationIndex, false);
    }

    removeAnchorPoints();
    restoreAllAnnotations();

    // Update mode state
    mode.value = { kind: "idle" };

    // Update sharedState (editMode computed will reflect this)
    sharedState.editModeActive.value = false;
    sharedState.currentAnnotationIndex.value = null;

    // Broadcast edit mode state to question component
    (answer as any).editModeState = false;
  };

  const editNextAnnotation = () => {
    if (!editMode.value.active || editMode.value.annotationIndex === null) return;
    
    const currentIndex = editMode.value.annotationIndex;
    const nextIndex = (currentIndex + 1) % annotations.value.length;
    
    enterEditMode(nextIndex);
  };

  const editPreviousAnnotation = () => {
    if (!editMode.value.active || editMode.value.annotationIndex === null) return;
    
    const currentIndex = editMode.value.annotationIndex;
    const prevIndex = currentIndex === 0 ? annotations.value.length - 1 : currentIndex - 1;
    
    enterEditMode(prevIndex);
  };

  const hideContextMenu = () => {
    contextMenu.value = {
      visible: false,
      x: 0,
      y: 0,
      annotationIndex: null,
      holeIndex: null,
    };
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
    
    // Delete the shape from the array
    answer.values.splice(index, 1);
    
    // Update answer - this triggers the watch on answer.values.length which re-renders the canvas
    updateAnswer();
  };

  const handleContextMenuDelete = () => {
    if (contextMenu.value.annotationIndex !== null) {
      deleteShape(contextMenu.value.annotationIndex);
      hideContextMenu();
    }
  };

  const handleContextMenuEdit = () => {
    if (contextMenu.value.annotationIndex !== null) {
      enterEditMode(contextMenu.value.annotationIndex);
    }
  };

  const handleContextMenuAddHole = () => {
    if (contextMenu.value.annotationIndex !== null) {
      enterHoleDrawingMode(contextMenu.value.annotationIndex);
      hideContextMenu();
    }
  };

  const handleContextMenuDeleteHole = () => {
    if (contextMenu.value.annotationIndex !== null && contextMenu.value.holeIndex !== null) {
      const annotation = annotations.value[contextMenu.value.annotationIndex];
      if (annotation && annotation.holes && annotation.holes[contextMenu.value.holeIndex]) {
        // Remove the hole
        annotation.holes.splice(contextMenu.value.holeIndex, 1);
        
        // Clean up if no holes left
        if (annotation.holes.length === 0) {
          delete annotation.holes;
        }
        
        // Update and re-render
        updateAnswer();
        renderAnnotations();
        
        // Update anchor points if in edit mode
        if (editMode.value.active && editMode.value.annotationIndex === contextMenu.value.annotationIndex) {
          renderAnchorPoints(contextMenu.value.annotationIndex);
        }
      }
      hideContextMenu();
    }
  };

  const enterHoleDrawingMode = (parentIndex: number) => {
    // Cancel any ongoing drawing using mode state
    if (mode.value.kind === "draw-poly" || mode.value.kind === "draw-hole-poly") {
      cancelPolygon();
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
      parentIndex: parentIndex,
    };

    // Highlight the parent shape
    highlightParentForHoleDrawing(parentIndex);

    // Fade other annotations
    fadeNonEditedAnnotations(parentIndex);
  };

  const exitHoleDrawingMode = () => {
    if (!sharedState.holeDrawingMode.value.active) return;

    // Cancel any ongoing polygon drawing using mode state
    if (mode.value.kind === "draw-hole-poly") {
      cancelPolygon();
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
    const { parentShape } = getAnnotationNodes(parentIndex);
    if (!parentShape) return;

    const annotation = annotations.value[parentIndex];
    const color = getAnnotationColor(annotation.label);

    (parentShape as any).strokeWidth(3);
    (parentShape as any).stroke(color);
    (parentShape as any).dash([10, 5]); // Dashed stroke to indicate hole drawing mode
    (parentShape as any).opacity(0.4);

    layer?.batchDraw();
    imageLayer?.batchDraw();
  };

  const fadeNonEditedAnnotations = (editingIndex: number) => {
    if (!layer) return;
    
    annotations.value.forEach((_, index) => {
      if (index !== editingIndex) {
        const { parentShape } = getAnnotationNodes(index);
        if (parentShape) {
          (parentShape as any).opacity(0.2);
        }
      }
    });
    
    layer.batchDraw();
  };

  const restoreAllAnnotations = () => {
    if (!layer) return;
    
    annotations.value.forEach((_, index) => {
      const { parentShape } = getAnnotationNodes(index);
      if (parentShape) {
        (parentShape as any).opacity(0.3);
      }
    });
    
    layer.batchDraw();
  };

  /**
   * Render a visual guide showing the parent shape boundary when editing holes
   */
  const renderParentBoundaryGuide = (annotationIndex: number, color: string) => {
    if (!layer) return;
    
    const annotation = annotations.value[annotationIndex];
    if (!annotation) return;
    
    const canvasPoints = getCanvasCoordinates(annotation.points);
    
    // Create a dashed boundary line to show the constraint
    let boundaryShape: Konva.Shape | null = null;
    
    if (annotation.shape_type === "rectangle" && canvasPoints.length === 2) {
      const [p1, p2] = canvasPoints;
      boundaryShape = new Konva.Rect({
        x: Math.min(p1[0], p2[0]),
        y: Math.min(p1[1], p2[1]),
        width: Math.abs(p2[0] - p1[0]),
        height: Math.abs(p2[1] - p1[1]),
        stroke: color,
        strokeWidth: 2,
        dash: [8, 4],
        opacity: 0.5,
        name: 'parent-boundary-guide',
        listening: false, // Don't interfere with interactions
      });
    } else if (annotation.shape_type === "polygon") {
      const points = canvasPoints.flat();
      boundaryShape = new Konva.Line({
        points,
        stroke: color,
        strokeWidth: 2,
        dash: [8, 4],
        opacity: 0.5,
        closed: true,
        name: 'parent-boundary-guide',
        listening: false,
      });
    }
    
    if (boundaryShape) {
      layer.add(boundaryShape);
      boundaryShape.moveToBottom(); // Keep it behind anchor points
    }
  };

  const renderAnchorPoints = (annotationIndex: number) => {
    if (!layer) return;
    
    // Remove existing anchor points
    removeAnchorPoints();
    
    const annotation = annotations.value[annotationIndex];
    if (!annotation) return;
    
    const color = getAnnotationColor(annotation.label);
    
    // Render anchor points for parent shape
    const canvasPoints = getCanvasCoordinates(annotation.points);
    
    // If editing a hole, show parent boundary as visual guide
    if (draggingPoint.value?.holeIndex !== null) {
      renderParentBoundaryGuide(annotationIndex, color);
    }
    
    // Create anchor points based on shape type
    if (annotation.shape_type === "rectangle" && canvasPoints.length === 2) {
      // Note: We use custom anchor points instead of Konva.Transformer for rectangles
      // because Transformer doesn't work properly with Groups that have holes (which use
      // composite operations like 'destination-out' for cutout effects)
      const [p1, p2] = canvasPoints;
      const corners = [
        { x: p1[0], y: p1[1] }, // top-left
        { x: p2[0], y: p1[1] }, // top-right
        { x: p2[0], y: p2[1] }, // bottom-right
        { x: p1[0], y: p2[1] }, // bottom-left
      ];
      
      corners.forEach((corner, pointIndex) => {
        createAnchorPoint(corner.x, corner.y, color, annotationIndex, pointIndex, null);
      });
    } else if (annotation.shape_type === "polygon") {
      // For polygons, render edge handles first (lower z-index)
      renderEdgeHandles(annotationIndex, canvasPoints, color, null);
      
      // Then show all vertex points (higher z-index)
      canvasPoints.forEach((point, pointIndex) => {
        createAnchorPoint(point[0], point[1], color, annotationIndex, pointIndex, null);
      });
    }
    
    // Render anchor points for holes if they exist
    if (annotation.holes && annotation.holes.length > 0) {
      annotation.holes.forEach((hole, holeIndex) => {
        const holeCanvasPoints = getCanvasCoordinates(hole.points);
        
        if (hole.shape_type === "rectangle" && holeCanvasPoints.length === 2) {
          const [p1, p2] = holeCanvasPoints;
          const corners = [
            { x: p1[0], y: p1[1] },
            { x: p2[0], y: p1[1] },
            { x: p2[0], y: p2[1] },
            { x: p1[0], y: p2[1] },
          ];
          
          corners.forEach((corner, pointIndex) => {
            createAnchorPoint(corner.x, corner.y, color, annotationIndex, pointIndex, holeIndex);
          });
        } else if (hole.shape_type === "polygon") {
          // Render edge handles for polygon holes
          renderEdgeHandles(annotationIndex, holeCanvasPoints, color, holeIndex);
          
          // Render vertex points for polygon holes
          holeCanvasPoints.forEach((point, pointIndex) => {
            createAnchorPoint(point[0], point[1], color, annotationIndex, pointIndex, holeIndex);
          });
        }
      });
    }
    
    layer.batchDraw();
  };

  const createAnchorPoint = (
    x: number, 
    y: number, 
    color: string, 
    annotationIndex: number, 
    pointIndex: number, 
    holeIndex: number | null
  ) => {
    const anchorId = holeIndex !== null 
      ? `anchor-${annotationIndex}-hole-${holeIndex}-${pointIndex}`
      : `anchor-${annotationIndex}-${pointIndex}`;
    
    const anchor = new Konva.Circle({
      x,
      y,
      radius: 6,
      fill: 'white',
      stroke: color,
      strokeWidth: 2,
      draggable: true,
      name: 'anchor-point',
      id: anchorId,
    });
    
    // Change cursor on hover
    anchor.on('mouseenter', () => {
      const stage = anchor.getStage();
      if (stage) {
        stage.container().style.cursor = 'move';
      }
      anchor.radius(8); // Make slightly larger on hover
      layer?.batchDraw();
    });
    
    anchor.on('mouseleave', () => {
      if (!draggingPoint.value) {
        const stage = anchor.getStage();
        if (stage) {
          stage.container().style.cursor = 'default';
        }
        anchor.radius(6);
        layer?.batchDraw();
      }
    });
    
    // Handle dragging
    anchor.on('dragstart', () => {
      draggingPoint.value = { annotationIndex, pointIndex, holeIndex };
    });
    
    anchor.on('dragmove', () => {
      if (draggingPoint.value) {
        const constrainedPosition = constrainPointToParentShape(
          annotationIndex,
          anchor.position(),
          holeIndex,
        );

        if (constrainedPosition.x !== anchor.x() || constrainedPosition.y !== anchor.y()) {
          anchor.position(constrainedPosition);
        }

        updateAnnotationFromDrag(annotationIndex, pointIndex, constrainedPosition, holeIndex);
        layer?.batchDraw();
      }
    });
    
    anchor.on('dragend', () => {
      if (draggingPoint.value) {
        finalizeAnnotationEdit(annotationIndex);
        draggingPoint.value = null;
        const stage = anchor.getStage();
        if (stage) {
          stage.container().style.cursor = 'default';
        }
      }
    });
    
    layer?.add(anchor);
  };

  const removeAnchorPoints = () => {
    if (!layer) return;
    layer.find('.anchor-point').forEach((anchor) => anchor.destroy());
    layer.find('.edge-handle').forEach((edge) => edge.destroy());
    layer.find('.parent-boundary-guide').forEach((guide) => guide.destroy());
    layer.batchDraw();
  };

  const renderEdgeHandles = (annotationIndex: number, canvasPoints: number[][], color: string, holeIndex: number | null) => {
    if (!layer) return;
    
    // Create edge handles between consecutive points
    for (let i = 0; i < canvasPoints.length; i++) {
      const startPoint = canvasPoints[i];
      const endPoint = canvasPoints[(i + 1) % canvasPoints.length]; // Wrap around to first point
      
      const edgeId = holeIndex !== null
        ? `edge-${annotationIndex}-hole-${holeIndex}-${i}`
        : `edge-${annotationIndex}-${i}`;
      
      // Create an invisible/semi-transparent line that's easier to click
      const edgeLine = new Konva.Line({
        points: [startPoint[0], startPoint[1], endPoint[0], endPoint[1]],
        stroke: color,
        strokeWidth: 16, // Thicker for easier clicking
        opacity: 0, // Invisible by default
        lineCap: 'round',
        lineJoin: 'round',
        name: 'edge-handle',
        id: edgeId,
      });
      
      // Hover effects
      edgeLine.on('mouseenter', () => {
        const stage = edgeLine.getStage();
        if (stage) {
          stage.container().style.cursor = 'copy'; // Indicate insertion
        }
        edgeLine.opacity(0.3); // Make visible on hover
        edgeLine.strokeWidth(4);
        layer?.batchDraw();
      });
      
      edgeLine.on('mouseleave', () => {
        const stage = edgeLine.getStage();
        if (stage) {
          stage.container().style.cursor = 'default';
        }
        edgeLine.opacity(0);
        edgeLine.strokeWidth(16);
        layer?.batchDraw();
      });
      
      // Click to insert point
      edgeLine.on('click', (e) => {
        const stage = edgeLine.getStage();
        if (!stage) return;
        
        const pointerPos = stage.getPointerPosition();
        if (!pointerPos) return;
        
        // Insert new point at click position
        insertPointOnEdge(annotationIndex, i, pointerPos, holeIndex);
      });
      
      layer.add(edgeLine);
    }
  };

  /**
   * Get the bounding box of a parent shape in image coordinates
   */
  const getParentShapeBounds = (parentPoints: number[][], parentShapeType: string) => {
    const xs = parentPoints.map(p => p[0]);
    const ys = parentPoints.map(p => p[1]);
    return {
      minX: Math.min(...xs),
      maxX: Math.max(...xs),
      minY: Math.min(...ys),
      maxY: Math.max(...ys),
    };
  };

  /**
   * Clamp a point to stay within parent shape bounds
   */
  const clampToParentBounds = (point: number[], parentBounds: { minX: number; maxX: number; minY: number; maxY: number }): number[] => {
    return [
      Math.max(parentBounds.minX, Math.min(parentBounds.maxX, point[0])),
      Math.max(parentBounds.minY, Math.min(parentBounds.maxY, point[1])),
    ];
  };

  const getParentShapeNode = (annotationIndex: number): Konva.Shape | null => {
    return getAnnotationNodes(annotationIndex).parentShape;
  };

  const getClosestPointOnPolygon = (
    point: Konva.Vector2d,
    polygonPoints: { x: number; y: number }[],
  ): Konva.Vector2d => {
    let closestPoint: Konva.Vector2d = { x: point.x, y: point.y };
    let minDistance = Infinity;

    if (polygonPoints.length < 2) {
      return closestPoint;
    }

    for (let i = 0; i < polygonPoints.length; i++) {
      const p1 = polygonPoints[i];
      const p2 = polygonPoints[(i + 1) % polygonPoints.length];

      const dx = p2.x - p1.x;
      const dy = p2.y - p1.y;

      if (dx === 0 && dy === 0) continue;

      const t = ((point.x - p1.x) * dx + (point.y - p1.y) * dy) / (dx * dx + dy * dy);
      const clampedT = Math.max(0, Math.min(1, t));

      const candidate = {
        x: p1.x + clampedT * dx,
        y: p1.y + clampedT * dy,
      };

      const distance = Math.hypot(point.x - candidate.x, point.y - candidate.y);

      if (distance < minDistance) {
        minDistance = distance;
        closestPoint = candidate;
      }
    }

    return closestPoint;
  };

  const constrainPointToParentShape = (
    annotationIndex: number,
    stagePoint: Konva.Vector2d,
    holeIndex: number | null,
  ): Konva.Vector2d => {
    const annotation = annotations.value[annotationIndex];
    if (!annotation) {
      return stagePoint;
    }

    // Only constrain when moving a hole point
    if (holeIndex === null) {
      return stagePoint;
    }

    if (annotation.shape_type === "rectangle") {
      const parentBounds = getParentShapeBounds(annotation.points, annotation.shape_type);
      const clampedImagePoint = clampToParentBounds(
        getImageCoordinates([[stagePoint.x, stagePoint.y]])[0],
        parentBounds,
      );
      const [canvasX, canvasY] = getCanvasCoordinates([clampedImagePoint])[0];
      return { x: canvasX, y: canvasY };
    }

    if (annotation.shape_type === "polygon") {
      const parentShape = getParentShapeNode(annotationIndex);
      if (parentShape && parentShape.intersects(stagePoint)) {
        return stagePoint;
      }

      const polygonCanvasPoints = getCanvasCoordinates(annotation.points).map(([x, y]) => ({ x, y }));
      return getClosestPointOnPolygon(stagePoint, polygonCanvasPoints);
    }

    return stagePoint;
  };

  const insertPointOnEdge = (
    annotationIndex: number,
    edgeIndex: number,
    position: { x: number; y: number },
    holeIndex: number | null,
  ) => {
    const annotation = annotations.value[annotationIndex];
    if (!annotation) return;

    const constrainedPos = constrainPointToParentShape(annotationIndex, position, holeIndex);

    // Convert canvas position to image coordinates
    let imageCoords = getImageCoordinates([[constrainedPos.x, constrainedPos.y]])[0];

    if (holeIndex !== null) {
      // Insert point into hole - clamp to parent bounds
      const hole = annotation.holes?.[holeIndex];
      if (hole && hole.shape_type === "polygon") {
        hole.points.splice(edgeIndex + 1, 0, imageCoords);
      }
    } else {
      // Insert point into parent shape
      if (annotation.shape_type === "polygon") {
        annotation.points.splice(edgeIndex + 1, 0, imageCoords);
      }
    }
    
    // Update the answer
    updateAnswer();
    
    // Re-render anchor points to show the new point
    renderAnchorPoints(annotationIndex);
    
    // Update the annotation shape
    updateAnnotationShape(annotationIndex);
  };

  const updateAnnotationFromDrag = (annotationIndex: number, pointIndex: number, newPos: { x: number; y: number }, holeIndex: number | null) => {
    const annotation = annotations.value[annotationIndex];
    if (!annotation) return;
    
    let imageCoords = getImageCoordinates([[newPos.x, newPos.y]])[0];

    if (holeIndex !== null) {
      // Update hole points - clamp to parent bounds
      const hole = annotation.holes?.[holeIndex];
      if (!hole) return;

      if (hole.shape_type === "rectangle") {
        const currentPoints = hole.points;
        
        if (pointIndex === 0) {
          hole.points = [imageCoords, currentPoints[1]];
        } else if (pointIndex === 1) {
          hole.points = [[currentPoints[0][0], imageCoords[1]], [imageCoords[0], currentPoints[1][1]]];
        } else if (pointIndex === 2) {
          hole.points = [currentPoints[0], imageCoords];
        } else if (pointIndex === 3) {
          hole.points = [[imageCoords[0], currentPoints[0][1]], [currentPoints[1][0], imageCoords[1]]];
        }
      } else if (hole.shape_type === "polygon") {
        hole.points[pointIndex] = imageCoords;
      }
    } else {
      // Update parent shape points
      if (annotation.shape_type === "rectangle") {
        const currentPoints = annotation.points;
        
        if (pointIndex === 0) {
          annotation.points = [imageCoords, currentPoints[1]];
        } else if (pointIndex === 1) {
          annotation.points = [[currentPoints[0][0], imageCoords[1]], [imageCoords[0], currentPoints[1][1]]];
        } else if (pointIndex === 2) {
          annotation.points = [currentPoints[0], imageCoords];
        } else if (pointIndex === 3) {
          annotation.points = [[imageCoords[0], currentPoints[0][1]], [currentPoints[1][0], imageCoords[1]]];
        }
      } else if (annotation.shape_type === "polygon") {
        annotation.points[pointIndex] = imageCoords;
      }
    }
    
    // Re-render the annotation shape in real-time
    updateAnnotationShape(annotationIndex);
  };

  const updateAnnotationShape = (annotationIndex: number) => {
    if (!layer) return;
    
    const { element, parentShape } = getAnnotationNodes(annotationIndex);
    if (!element || !parentShape) return;
    
    const annotation = annotations.value[annotationIndex];
    const canvasPoints = getCanvasCoordinates(annotation.points);
    
    // Update parent shape
    if (annotation.shape_type === "rectangle" && canvasPoints.length === 2) {
      const [p1, p2] = canvasPoints;
      (parentShape as Konva.Rect).x(Math.min(p1[0], p2[0]));
      (parentShape as Konva.Rect).y(Math.min(p1[1], p2[1]));
      (parentShape as Konva.Rect).width(Math.abs(p2[0] - p1[0]));
      (parentShape as Konva.Rect).height(Math.abs(p2[1] - p1[1]));
    } else if (annotation.shape_type === "polygon") {
      const points = canvasPoints.flat();
      (parentShape as Konva.Line).points(points);
    }
    
    // Update hole shapes if they exist
    if (element instanceof Konva.Group && annotation.holes && annotation.holes.length > 0) {
      annotation.holes.forEach((hole, holeIndex) => {
        const holeShape = element.findOne(`#annotation-${annotationIndex}-hole-${holeIndex}`);
        if (!holeShape) return;
        
        const holeCanvasPoints = getCanvasCoordinates(hole.points);
        
        if (hole.shape_type === "rectangle" && holeCanvasPoints.length === 2) {
          const [p1, p2] = holeCanvasPoints;
          (holeShape as Konva.Rect).x(Math.min(p1[0], p2[0]));
          (holeShape as Konva.Rect).y(Math.min(p1[1], p2[1]));
          (holeShape as Konva.Rect).width(Math.abs(p2[0] - p1[0]));
          (holeShape as Konva.Rect).height(Math.abs(p2[1] - p1[1]));
        } else if (hole.shape_type === "polygon") {
          const points = holeCanvasPoints.flat();
          (holeShape as Konva.Line).points(points);
        }
      });
    }
    
    layer.batchDraw();
  };

  const finalizeAnnotationEdit = (annotationIndex: number) => {
    // Save the changes
    updateAnswer();
    
    // Re-render anchor points at new positions
    renderAnchorPoints(annotationIndex);
  };

  const initCanvas = () => {
    if (!canvasContainer.value) return;

    const containerWidth = canvasContainer.value.offsetWidth;
    const containerHeight = canvasContainer.value.offsetHeight || 500;

    stage = new Konva.Stage({
      container: canvasContainer.value,
      width: containerWidth,
      height: containerHeight,
    });

    imageLayer = new Konva.Layer();
    layer = new Konva.Layer();

    stage.add(imageLayer);
    stage.add(layer);

    loadImage();
    setupEventHandlers();
  };

  const loadImage = () => {
    const img = new Image();
    img.crossOrigin = "anonymous";

    img.onload = () => {
      if (!stage || !layer) return;

      // Store original image dimensions
      originalImageWidth = img.width;
      originalImageHeight = img.height;

      const stageWidth = stage.width();
      const stageHeight = stage.height();

      // Calculate scale to fit image in canvas
      const scale = Math.min(
        stageWidth / img.width,
        stageHeight / img.height,
        1 // Don't scale up
      );

      imageNode = new Konva.Image({
        image: img,
        x: (stageWidth - img.width * scale) / 2,
        y: (stageHeight - img.height * scale) / 2,
        width: img.width * scale,
        height: img.height * scale,
      });

      imageLayer?.add(imageNode);
      imageLayer?.batchDraw();

      imageLoaded.value = true;
      renderAnnotations();
    };

    img.onerror = () => {
      hasError.value = true;
    };

    img.src = content;
  };

  const setupEventHandlers = () => {
    if (!stage) return;

    stage.on("mousedown touchstart", handleMouseDown);
    stage.on("mousemove touchmove", handleMouseMove);
    stage.on("mouseup touchend", handleMouseUp);
    
    // Add keyboard event listener for polygon mode
    window.addEventListener("keydown", handleKeyDown);
  };

  const createPointCircle = (x: number, y: number, color?: string): Konva.Circle => {
    return new Konva.Circle({
      x,
      y,
      radius: 5,
      fill: color || selectedLabel.value?.color || "#cccccc",
      stroke: "white",
      strokeWidth: 2,
    });
  };

  const completePolygon = () => {
    if (mode.value.kind !== "draw-poly" && mode.value.kind !== "draw-hole-poly") return;
    if (mode.value.points.length < 6) return;

    // Convert flat array to point pairs
    const points: number[][] = [];
    for (let i = 0; i < mode.value.points.length; i += 2) {
      points.push([mode.value.points[i], mode.value.points[i + 1]]);
    }

    // Convert to image coordinates
    const imageCoords = getImageCoordinates(points);

    if (mode.value.kind === "draw-hole-poly") {
      // Create hole and add to parent
      const parent = annotations.value[mode.value.parentIndex];
      if (!parent.holes) {
        parent.holes = [];
      }

      parent.holes.push({
        points: imageCoords,
        shape_type: "polygon",
        flags: {},
      });

      updateAnswer();
      cleanupPolygonDrawing();
      renderAnnotations();
      
      // Stay in hole drawing mode for adding more holes
      highlightParentForHoleDrawing(mode.value.parentIndex);
    } else {
      // Normal annotation creation
      if (!selectedLabel.value) return;

      const annotation: ImageAnnotationAnswer = {
        label: selectedLabel.value.value,
        points: imageCoords,
        shape_type: "polygon",
        flags: {},
      };

      answer.values.push(annotation);
      updateAnswer();
      cleanupPolygonDrawing();
      renderAnnotations();
    }

    mode.value = { kind: "idle" };
  };

  const cancelPolygon = () => {
    cleanupPolygonDrawing();
    mode.value = { kind: "idle" };
    layer?.batchDraw();
  };

  const cleanupPolygonDrawing = () => {
    // Remove drawing shape
    if (drawingShape) {
      drawingShape.destroy();
      drawingShape = null;
    }

    // Remove preview line
    if (polygonPreviewLine) {
      polygonPreviewLine.destroy();
      polygonPreviewLine = null;
    }

    // Remove point circles
    polygonPointCircles.forEach((circle) => circle.destroy());
    polygonPointCircles = [];

    // Reset state
    polygonPoints = [];
    isDrawingPolygon = false;
  };

  const isPointWithinParent = (point: { x: number; y: number }, parentIndex: number): boolean => {
    const parent = annotations.value[parentIndex];
    if (!parent) return false;

    const canvasPoints = getCanvasCoordinates(parent.points);
    
    // Get bounding box of parent
    const xs = canvasPoints.map(p => p[0]);
    const ys = canvasPoints.map(p => p[1]);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);

    // Check if point is within bounding box
    return point.x >= minX && point.x <= maxX && point.y >= minY && point.y <= maxY;
  };

  const handleMouseDown = (e: Konva.KonvaEventObject<MouseEvent>) => {
    const pos = stage?.getPointerPosition();
    if (!pos) return;

    // Use mode state machine for cleaner logic
    switch (mode.value.kind) {
      case "idle": {
        // Check if in hole drawing mode
        const inHoleMode = sharedState.holeDrawingMode.value.active;
        const parentIndex = sharedState.holeDrawingMode.value.parentIndex;

        if (inHoleMode && parentIndex !== null) {
          // Validate point is within parent bounds
          if (!isPointWithinParent(pos, parentIndex)) {
            return; // Ignore clicks outside parent bounds
          }

          const drawColor = getAnnotationColor(annotations.value[parentIndex].label);

          // Start hole drawing
          if (selectedTool.value === "rectangle") {
            mode.value = { kind: "draw-hole-rect", parentIndex, start: pos, color: drawColor };
            
            drawingShape = new Konva.Rect({
              x: pos.x,
              y: pos.y,
              width: 0,
              height: 0,
              stroke: drawColor,
              strokeWidth: 2,
              dash: [5, 5],
            });
            layer?.add(drawingShape);
            layer?.batchDraw();
          } else if (selectedTool.value === "polygon") {
            const circle = createPointCircle(pos.x, pos.y, drawColor);
            const previewLine = new Konva.Line({
              points: [pos.x, pos.y, pos.x, pos.y],
              stroke: drawColor,
              strokeWidth: 2,
              dash: [5, 5],
            });
            layer?.add(previewLine);

            mode.value = {
              kind: "draw-hole-poly",
              parentIndex,
              color: drawColor,
              points: [pos.x, pos.y],
              circles: [circle],
              previewLine,
            };

            // Keep old flags in sync
            isDrawingPolygon = true;
            polygonPoints = [pos.x, pos.y];
            polygonPointCircles = [circle];
            polygonPreviewLine = previewLine;

            drawingShape = new Konva.Line({
              points: [pos.x, pos.y],
              stroke: drawColor,
              strokeWidth: 2,
              fill: drawColor,
              opacity: 0.3,
              closed: false,
            });
            layer?.add(drawingShape);
            layer?.add(circle);
            layer?.batchDraw();
          }
        } else {
          // Normal drawing mode - need label selected
          if (!selectedLabel.value) {
            alert("Please select a label first");
            return;
          }

          const drawColor = selectedLabel.value.color || "#cccccc";

          // Start normal drawing
          if (selectedTool.value === "rectangle") {
            mode.value = { kind: "draw-rect", start: pos, color: drawColor };
            
            drawingShape = new Konva.Rect({
              x: pos.x,
              y: pos.y,
              width: 0,
              height: 0,
              stroke: drawColor,
              strokeWidth: 2,
              dash: [5, 5],
            });
            layer?.add(drawingShape);
            layer?.batchDraw();
          } else if (selectedTool.value === "polygon") {
            const circle = createPointCircle(pos.x, pos.y, drawColor);
            const previewLine = new Konva.Line({
              points: [pos.x, pos.y, pos.x, pos.y],
              stroke: drawColor,
              strokeWidth: 2,
              dash: [5, 5],
            });
            layer?.add(previewLine);

            mode.value = {
              kind: "draw-poly",
              color: drawColor,
              points: [pos.x, pos.y],
              circles: [circle],
              previewLine,
            };

            // Keep old flags in sync
            isDrawingPolygon = true;
            polygonPoints = [pos.x, pos.y];
            polygonPointCircles = [circle];
            polygonPreviewLine = previewLine;

            drawingShape = new Konva.Line({
              points: [pos.x, pos.y],
              stroke: drawColor,
              strokeWidth: 2,
              fill: drawColor,
              opacity: 0.3,
              closed: false,
            });
            layer?.add(drawingShape);
            layer?.add(circle);
            layer?.batchDraw();
          }
        }
        break;
      }

      case "draw-poly": {
        // Check if clicking near first point (close polygon)
        const firstPoint = { x: mode.value.points[0], y: mode.value.points[1] };
        const distance = Math.sqrt(
          Math.pow(pos.x - firstPoint.x, 2) + Math.pow(pos.y - firstPoint.y, 2)
        );

        if (distance < CLOSE_THRESHOLD && mode.value.points.length >= 6) {
          completePolygon();
          return;
        }

        // Add new point
        mode.value.points.push(pos.x, pos.y);
        (drawingShape as Konva.Line)?.points(mode.value.points);

        // Add point circle
        const circle = createPointCircle(pos.x, pos.y, mode.value.color);
        mode.value.circles.push(circle);
        layer?.add(circle);
        layer?.batchDraw();
        break;
      }

      case "draw-hole-poly": {
        // Check if clicking near first point (close polygon)
        const firstPoint = { x: mode.value.points[0], y: mode.value.points[1] };
        const distance = Math.sqrt(
          Math.pow(pos.x - firstPoint.x, 2) + Math.pow(pos.y - firstPoint.y, 2)
        );

        if (distance < CLOSE_THRESHOLD && mode.value.points.length >= 6) {
          completePolygon();
          return;
        }

        // Add new point
        mode.value.points.push(pos.x, pos.y);
        (drawingShape as Konva.Line)?.points(mode.value.points);

        // Add point circle
        const circle = createPointCircle(pos.x, pos.y, mode.value.color);
        mode.value.circles.push(circle);
        layer?.add(circle);
        layer?.batchDraw();
        break;
      }

      case "edit":
      case "draw-rect":
      case "draw-hole-rect":
        // These modes don't handle additional clicks
        break;
    }
  };

  const handleMouseMove = (e: Konva.KonvaEventObject<MouseEvent>) => {
    const pos = stage?.getPointerPosition();
    if (!pos) return;

    switch (mode.value.kind) {
      case "draw-rect":
      case "draw-hole-rect": {
        if (drawingShape) {
          const width = pos.x - mode.value.start.x;
          const height = pos.y - mode.value.start.y;

          (drawingShape as Konva.Rect).width(width);
          (drawingShape as Konva.Rect).height(height);

          layer?.batchDraw();
        }
        break;
      }

      case "draw-poly":
      case "draw-hole-poly": {
        if (mode.value.previewLine) {
          // Update preview line from last point to cursor
          const lastX = mode.value.points[mode.value.points.length - 2];
          const lastY = mode.value.points[mode.value.points.length - 1];

          mode.value.previewLine.points([lastX, lastY, pos.x, pos.y]);

          // Highlight first point if cursor is near it (and we have at least 3 points)
          if (mode.value.points.length >= 6 && mode.value.circles.length > 0) {
            const firstPoint = { x: mode.value.points[0], y: mode.value.points[1] };
            const distance = Math.sqrt(
              Math.pow(pos.x - firstPoint.x, 2) + Math.pow(pos.y - firstPoint.y, 2)
            );

            if (distance < CLOSE_THRESHOLD) {
              // Highlight first point circle
              mode.value.circles[0].radius(8);
              mode.value.circles[0].fill("white");
              mode.value.circles[0].stroke(mode.value.color);
            } else {
              // Reset first point circle
              mode.value.circles[0].radius(5);
              mode.value.circles[0].fill(mode.value.color);
              mode.value.circles[0].stroke("white");
            }
          }

          layer?.batchDraw();
        }
        break;
      }

      case "idle":
      case "edit":
        // No drawing in progress
        break;
    }
  };

  const handleMouseUp = (e: Konva.KonvaEventObject<MouseEvent>) => {
    const pos = stage?.getPointerPosition();
    if (!pos || !drawingShape) return;

    // Use mode state machine for cleaner logic
    switch (mode.value.kind) {
      case "draw-rect": {
        const width = pos.x - mode.value.start.x;
        const height = pos.y - mode.value.start.y;

        // Minimum size check
        if (Math.abs(width) < 5 || Math.abs(height) < 5) {
          drawingShape.destroy();
          drawingShape = null;
          layer?.batchDraw();
          mode.value = { kind: "idle" };
          isDrawing = false; // Keep old flag in sync
          return;
        }

        // Convert to image coordinates
        const imageCoords = getImageCoordinates([
          [mode.value.start.x, mode.value.start.y],
          [pos.x, pos.y],
        ]);

        // Normal annotation creation
        if (!selectedLabel.value) {
          mode.value = { kind: "idle" };
          isDrawing = false;
          return;
        }

        const annotation: ImageAnnotationAnswer = {
          label: selectedLabel.value.value,
          points: imageCoords,
          shape_type: "rectangle",
          flags: {},
        };

        answer.values.push(annotation);
        updateAnswer();
        drawingShape.destroy();
        drawingShape = null;
        renderAnnotations();

        mode.value = { kind: "idle" };
        break;
      }

      case "draw-hole-rect": {
        const width = pos.x - mode.value.start.x;
        const height = pos.y - mode.value.start.y;

        // Minimum size check
        if (Math.abs(width) < 5 || Math.abs(height) < 5) {
          drawingShape.destroy();
          drawingShape = null;
          layer?.batchDraw();
          mode.value = { kind: "idle" };
          isDrawing = false; // Keep old flag in sync
          return;
        }

        // Convert to image coordinates
        const imageCoords = getImageCoordinates([
          [mode.value.start.x, mode.value.start.y],
          [pos.x, pos.y],
        ]);

        // Create hole and add to parent
        const parent = annotations.value[mode.value.parentIndex];
        if (!parent.holes) {
          parent.holes = [];
        }

        parent.holes.push({
          points: imageCoords,
          shape_type: "rectangle",
          flags: {},
        });

        updateAnswer();
        drawingShape.destroy();
        drawingShape = null;
        renderAnnotations();
        
        // Stay in hole drawing mode for adding more holes
        highlightParentForHoleDrawing(mode.value.parentIndex);

        mode.value = { kind: "idle" };
        break;
      }

      case "idle":
      case "edit":
      case "draw-poly":
      case "draw-hole-poly":
        // These modes don't handle mouse up for rectangles
        break;
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    switch (mode.value.kind) {
      case "draw-hole-poly":
        if (e.key === "Escape") {
          e.preventDefault();
          cancelPolygon();
          return;
        } else if (e.key === "Enter" && mode.value.points.length >= 6) {
          e.preventDefault();
          completePolygon();
          return;
        }
        break;

      case "draw-hole-rect":
        if (e.key === "Escape") {
          e.preventDefault();
          exitHoleDrawingMode();
          return;
        }
        break;

      case "edit":
        if (e.key === "Escape") {
          e.preventDefault();
          exitEditMode();
          return;
        } else if (e.key === "ArrowRight" || e.key.toLowerCase() === "n") {
          e.preventDefault();
          editNextAnnotation();
          return;
        } else if (e.key === "ArrowLeft" || e.key.toLowerCase() === "p") {
          e.preventDefault();
          editPreviousAnnotation();
          return;
        } else if (e.key === "Delete" || e.key === "Backspace") {
          e.preventDefault();
          if (mode.value.index !== null) {
            const indexToDelete = mode.value.index;
            // Move to next annotation or exit if this was the last one
            if (annotations.value.length > 1) {
              editNextAnnotation();
            } else {
              exitEditMode();
            }
            deleteShape(indexToDelete);
          }
          return;
        }
        break;

      case "draw-poly":
        if (e.key === "Escape") {
          e.preventDefault();
          cancelPolygon();
          return;
        } else if (e.key === "Enter" && mode.value.points.length >= 6) {
          e.preventDefault();
          completePolygon();
          return;
        }
        break;

      case "idle":
      case "draw-rect":
        // No keyboard shortcuts in these modes
        break;
    }
  };

  const getImageCoordinates = (canvasPoints: number[][]): number[][] => {
    if (!imageNode) return canvasPoints;

    const imageX = imageNode.x();
    const imageY = imageNode.y();
    const imageWidth = imageNode.width();
    const imageHeight = imageNode.height();
    const img = imageNode.image() as HTMLImageElement;

    return canvasPoints.map(([x, y]) => [
      ((x - imageX) / imageWidth) * (img?.width || 1),
      ((y - imageY) / imageHeight) * (img?.height || 1),
    ]);
  };

  const getCanvasCoordinates = (imagePoints: number[][]): number[][] => {
    if (!imageNode) return imagePoints;

    const imageX = imageNode.x();
    const imageY = imageNode.y();
    const imageWidth = imageNode.width();
    const imageHeight = imageNode.height();
    const img = imageNode.image() as HTMLImageElement;
    const originalWidth = img?.width || 1;
    const originalHeight = img?.height || 1;

    return imagePoints.map(([x, y]) => [
      (x / originalWidth) * imageWidth + imageX,
      (y / originalHeight) * imageHeight + imageY,
    ]);
  };

  const renderAnnotations = () => {
    if (!layer) return;

    // Remove existing annotation shapes and groups
    layer.find(".annotation-shape").forEach((shape) => shape.destroy());
    layer.find(".annotation-group").forEach((group) => group.destroy());

    // Render each annotation
    annotations.value.forEach((annotation, index) => {
      const color = getAnnotationColor(annotation.label);
      const canvasPoints = getCanvasCoordinates(annotation.points);

      // Check if annotation has holes
      const hasHoles = annotation.holes && annotation.holes.length > 0;

      if (hasHoles) {
        // Create a group for annotation with holes
        const group = new Konva.Group({
          id: `annotation-${index}`,
          name: "annotation-group",
        });

        // Create parent shape
        const parentShape = createShape(annotation.shape_type, canvasPoints, color, index, true);
        if (parentShape) {
          group.add(parentShape);
        }

        // Render holes as cutouts
        annotation.holes!.forEach((hole, holeIndex) => {
          const holeCanvasPoints = getCanvasCoordinates(hole.points);
          const holeShape = createShape(hole.shape_type, holeCanvasPoints, color, index, false, holeIndex);
          
          if (holeShape) {
            // Add context menu for holes
            holeShape.on('contextmenu', (e) => {
              e.evt.preventDefault();
              e.cancelBubble = true; // Prevent parent group from handling
              const stage = holeShape.getStage();
              if (stage) {
                const pointerPos = stage.getPointerPosition();
                if (pointerPos) {
                  const container = stage.container();
                  const rect = container.getBoundingClientRect();
                  showContextMenu(index, rect.left + pointerPos.x, rect.top + pointerPos.y, holeIndex);
                }
              }
            });
            
            // Use composite operation to create cutout effect
            holeShape.globalCompositeOperation('destination-out');
            group.add(holeShape);
          }
        });

        // Add event listeners to the group
        group.on('mouseenter', () => {
          hoverAnnotation(index);
        });

        group.on('mouseleave', () => {
          unhoverAnnotation();
        });

        group.on('contextmenu', (e) => {
          e.evt.preventDefault();
          const stage = group.getStage();
          if (stage) {
            const pointerPos = stage.getPointerPosition();
            if (pointerPos) {
              const container = stage.container();
              const rect = container.getBoundingClientRect();
              showContextMenu(index, rect.left + pointerPos.x, rect.top + pointerPos.y);
            }
          }
        });

        layer?.add(group);
      } else {
        // No holes - render as before
        const shape = createShape(annotation.shape_type, canvasPoints, color, index, true);

        if (shape) {
          // Add hover event listeners
          shape.on('mouseenter', () => {
            hoverAnnotation(index);
          });

          shape.on('mouseleave', () => {
            unhoverAnnotation();
          });

          // Add right-click context menu
          shape.on('contextmenu', (e) => {
            e.evt.preventDefault();
            const stage = shape?.getStage();
            if (stage) {
              const pointerPos = stage.getPointerPosition();
              if (pointerPos) {
                // Convert stage coordinates to page coordinates
                const container = stage.container();
                const rect = container.getBoundingClientRect();
                showContextMenu(index, rect.left + pointerPos.x, rect.top + pointerPos.y);
              }
            }
          });

          layer?.add(shape);
        }
      }
    });

    layer.batchDraw();
  };

  const createShape = (
    shapeType: string,
    canvasPoints: number[][],
    color: string,
    annotationIndex: number,
    isParent: boolean,
    holeIndex?: number
  ): Konva.Rect | Konva.Line | null => {
    const shapeId = isParent 
      ? `annotation-${annotationIndex}` 
      : `annotation-${annotationIndex}-hole-${holeIndex}`;
    const shapeName = isParent ? "annotation-shape" : "annotation-hole";

    if (shapeType === "rectangle" && canvasPoints.length === 2) {
      const [p1, p2] = canvasPoints;
      return new Konva.Rect({
        id: shapeId,
        name: shapeName,
        x: Math.min(p1[0], p2[0]),
        y: Math.min(p1[1], p2[1]),
        width: Math.abs(p2[0] - p1[0]),
        height: Math.abs(p2[1] - p1[1]),
        stroke: color,
        strokeWidth: 2,
        fill: color,
        opacity: isParent ? 0.3 : 1, // Holes are fully opaque for cutout
        listening: true,
      });
    } else if (shapeType === "polygon") {
      const points = canvasPoints.flat();
      return new Konva.Line({
        id: shapeId,
        name: shapeName,
        points: points,
        stroke: color,
        strokeWidth: 2,
        fill: color,
        opacity: isParent ? 0.3 : 1, // Holes are fully opaque for cutout
        closed: true,
        listening: true,
      });
    }

    return null;
  };

  const updateAnswer = () => {
    imageAnnotationQuestion.answer.response({
      value: answer.valuesAnswered,
    });
  };

  const resizeCanvas = () => {
    if (!stage || !canvasContainer.value || !imageNode) return;
    
    // Get new container dimensions
    const containerWidth = canvasContainer.value.offsetWidth;
    const containerHeight = canvasContainer.value.offsetHeight;
    
    if (containerWidth === 0 || containerHeight === 0) return;
    
    // Update stage size
    stage.width(containerWidth);
    stage.height(containerHeight);
    
    // Recalculate scale for image
    const scale = Math.min(
      containerWidth / originalImageWidth,
      containerHeight / originalImageHeight,
      1 // Don't scale up
    );
    
    // Recenter and rescale image
    imageNode.x((containerWidth - originalImageWidth * scale) / 2);
    imageNode.y((containerHeight - originalImageHeight * scale) / 2);
    imageNode.width(originalImageWidth * scale);
    imageNode.height(originalImageHeight * scale);
    
    // Re-render annotations
    renderAnnotations();
    
    // If in edit mode, re-render anchor points
    if (editMode.value.active && editMode.value.annotationIndex !== null) {
      renderAnchorPoints(editMode.value.annotationIndex);
    }
    
    layer?.batchDraw();
  };

  // Watch for changes in annotations from the question component
  watch(
    () => answer.values.length,
    () => {
      renderAnnotations();
    }
  );

  // Watch for cancel polygon signal from question component
  watch(
    () => (answer as any).cancelPolygon,
    (shouldCancel) => {
      if (shouldCancel && (mode.value.kind === "draw-poly" || mode.value.kind === "draw-hole-poly")) {
        cancelPolygon();
      }
    }
  );

  // Watch for enter edit mode signal from question component
  watch(sharedState.enterEditModeSignal, (editModeData) => {
    if (editModeData && editModeData.index !== null && editModeData.index !== undefined) {
      enterEditMode(editModeData.index);
    }
  });

  // Watch for exit edit mode signal from question component
  watch(sharedState.exitEditModeSignal, (shouldExit) => {
    if (shouldExit && editMode.value.active) {
      exitEditMode();
    }
  });

  // Watch for delete shape signal from question component
  watch(sharedState.deleteShapeSignal, (deleteSignal) => {
    if (deleteSignal && deleteSignal.index !== null && deleteSignal.index !== undefined) {
      deleteShape(deleteSignal.index);
    }
  });

  // Watch for delete hole signal from question component
  watch(sharedState.deleteHoleSignal, (deleteSignal) => {
    if (deleteSignal && deleteSignal.annotationIndex !== null && deleteSignal.holeIndex !== null) {
      const annotation = annotations.value[deleteSignal.annotationIndex];
      if (annotation && annotation.holes && annotation.holes[deleteSignal.holeIndex]) {
        // Remove the hole from the array
        annotation.holes.splice(deleteSignal.holeIndex, 1);
        
        // If no holes left, remove the holes array
        if (annotation.holes.length === 0) {
          delete annotation.holes;
        }
        
        // Update the answer
        updateAnswer();
        
        // Re-render the canvas
        renderAnnotations();
        
        // If in edit mode for this annotation, re-render anchor points
        if (editMode.value.active && editMode.value.annotationIndex === deleteSignal.annotationIndex) {
          renderAnchorPoints(deleteSignal.annotationIndex);
        }
      }
    }
  });

  // Watch for label reassignment in edit mode
  watch(sharedState.reassignLabel, (reassignData) => {
    if (reassignData && editMode.value.active && editMode.value.annotationIndex !== null) {
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

  onMounted(() => {
    initCanvas();

    // Handle window resize with debouncing
    const handleResize = () => {
      if (resizeTimeout) clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        resizeCanvas();
      }, 150); // Wait 150ms after last resize event
    };
    
    window.addEventListener("resize", handleResize);

    // Watch for container size changes (e.g., from resizable bar)
    if (canvasContainer.value) {
      resizeObserver = new ResizeObserver(() => {
        handleResize();
      });
      resizeObserver.observe(canvasContainer.value);
    }

    // Close context menu on click outside
    document.addEventListener('click', hideContextMenu);
  });

  onUnmounted(() => {
    window.removeEventListener("keydown", handleKeyDown);
    clearInterval(toolPollInterval);
    if (resizeTimeout) clearTimeout(resizeTimeout);
    if (resizeObserver) resizeObserver.disconnect();
    document.removeEventListener('click', hideContextMenu);
    stage?.destroy();
  });

  return {
    canvasContainer,
    imageLoaded,
    hasError,
    contextMenu,
    editMode,
    deleteShape, // Core deletion function - single source of truth
    handleContextMenuDelete,
    handleContextMenuEdit,
    handleContextMenuAddHole,
    handleContextMenuDeleteHole,
    enterEditMode,
    exitEditMode,
    exitHoleDrawingMode,
    editNextAnnotation,
    editPreviousAnnotation,
  };
};
