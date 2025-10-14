import { ref, computed, onMounted, watch, onUnmounted } from "vue-demi";
import Konva from "konva";
import { useImageAnnotationSharedState } from "./useImageAnnotationSharedState";
import {
  getImageCoordinates as getImageCoords,
  getCanvasCoordinates as getCanvasCoords,
} from "./coordinateTransformUtils";
import {
  getParentShapeBounds,
  clampToParentBounds,
  getClosestPointOnPolygon,
  isPointWithinParent as checkPointWithinParent,
} from "./geometryUtils";
import {
  getAnnotationNodes as getAnnotationNodesUtil,
  getParentShapeNode as getParentShapeNodeUtil,
  createShape,
  updateKonvaShape,
  updateRectanglePoint,
  createPointCircle,
  type AnnotationNodes,
} from "./konvaShapeUtils";
import { Question } from "~/v1/domain/entities/question/Question";
import { ImageAnnotationQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";
import { ImageAnnotationAnswer } from "~/v1/domain/entities/IAnswer";

type Mode =
  | { kind: "idle" }
  | { kind: "draw-rect"; start: { x: number; y: number }; color: string }
  | {
      kind: "draw-poly";
      color: string;
      points: number[];
      circles: Konva.Circle[];
      previewLine: Konva.Line | null;
    }
  | { kind: "edit"; index: number }
  | {
      kind: "draw-hole-poly";
      parentIndex: number;
      color: string;
      points: number[];
      circles: Konva.Circle[];
      previewLine: Konva.Line | null;
    }
  | {
      kind: "draw-hole-rect";
      parentIndex: number;
      start: { x: number; y: number };
      color: string;
    };

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
  const contextMenu = ref<{
    visible: boolean;
    x: number;
    y: number;
    annotationIndex: number | null;
    holeIndex: number | null;
  }>({
    visible: false,
    x: 0,
    y: 0,
    annotationIndex: null,
    holeIndex: null,
  });
  const draggingPoint = ref<{
    annotationIndex: number;
    pointIndex: number;
    holeIndex: number | null;
  } | null>(null);

  const mode = ref<Mode>({ kind: "idle" });

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

  const answer =
    imageAnnotationQuestion.answer as ImageAnnotationQuestionAnswer;

  const annotations = computed(() => answer.values);

  const sharedState = useImageAnnotationSharedState(answer);

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

  const getAnnotationNodes = (index: number): AnnotationNodes => {
    return getAnnotationNodesUtil(layer, index);
  };

  const highlightAnnotation = (index: number, highlight: boolean) => {
    const { element, parentShape, holeShapes } = getAnnotationNodes(index);
    if (!element || !parentShape) return;

    const isEditing =
      editMode.value.active && editMode.value.annotationIndex === index;
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
      stage.container().style.cursor = highlight ? "pointer" : "default";
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

  const showContextMenu = (
    index: number,
    x: number,
    y: number,
    holeIndex: number | null = null
  ) => {
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
    if (
      mode.value.kind === "draw-poly" ||
      mode.value.kind === "draw-hole-poly"
    ) {
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
      sharedState.selectLabelData.value = {
        labelValue: annotation.label,
      };
      sharedState.selectLabelTrigger.value++;
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
    if (
      contextMenu.value.annotationIndex !== null &&
      contextMenu.value.holeIndex !== null
    ) {
      const annotation = annotations.value[contextMenu.value.annotationIndex];
      if (
        annotation &&
        annotation.holes &&
        annotation.holes[contextMenu.value.holeIndex]
      ) {
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
        if (
          editMode.value.active &&
          editMode.value.annotationIndex === contextMenu.value.annotationIndex
        ) {
          renderAnchorPoints(contextMenu.value.annotationIndex);
        }
      }
      hideContextMenu();
    }
  };

  const enterHoleDrawingMode = (parentIndex: number) => {
    // Cancel any ongoing drawing using mode state
    if (
      mode.value.kind === "draw-poly" ||
      mode.value.kind === "draw-hole-poly"
    ) {
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
      parentIndex,
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
  const renderParentBoundaryGuide = (
    annotationIndex: number,
    color: string
  ) => {
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
        name: "parent-boundary-guide",
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
        name: "parent-boundary-guide",
        listening: false,
      });
    }

    if (boundaryShape) {
      layer.add(boundaryShape);
      boundaryShape.moveToBottom(); // Keep it behind anchor points
    }
  };

  // Helper to render anchor points for a shape (parent or hole)
  const renderShapeAnchors = (
    shapeType: string,
    canvasPoints: number[][],
    color: string,
    annotationIndex: number,
    holeIndex: number | null
  ) => {
    if (shapeType === "rectangle" && canvasPoints.length === 2) {
      const [p1, p2] = canvasPoints;
      const corners = [
        { x: p1[0], y: p1[1] }, // top-left
        { x: p2[0], y: p1[1] }, // top-right
        { x: p2[0], y: p2[1] }, // bottom-right
        { x: p1[0], y: p2[1] }, // bottom-left
      ];
      corners.forEach((corner, pointIndex) => {
        createAnchorPoint(
          corner.x,
          corner.y,
          color,
          annotationIndex,
          pointIndex,
          holeIndex
        );
      });
    } else if (shapeType === "polygon") {
      renderEdgeHandles(annotationIndex, canvasPoints, color, holeIndex);
      canvasPoints.forEach((point, pointIndex) => {
        createAnchorPoint(
          point[0],
          point[1],
          color,
          annotationIndex,
          pointIndex,
          holeIndex
        );
      });
    }
  };

  const renderAnchorPoints = (annotationIndex: number) => {
    if (!layer) return;

    removeAnchorPoints();

    const annotation = annotations.value[annotationIndex];
    if (!annotation) return;

    const color = getAnnotationColor(annotation.label);

    // Show parent boundary guide if editing a hole
    if (draggingPoint.value?.holeIndex !== null) {
      renderParentBoundaryGuide(annotationIndex, color);
    }

    // Render parent shape anchors
    // Note: We use custom anchor points instead of Konva.Transformer for rectangles
    // because Transformer doesn't work properly with Groups that have holes (which use
    // composite operations like 'destination-out' for cutout effects)
    const canvasPoints = getCanvasCoordinates(annotation.points);
    renderShapeAnchors(
      annotation.shape_type,
      canvasPoints,
      color,
      annotationIndex,
      null
    );

    // Render hole anchors
    annotation.holes?.forEach((hole, holeIndex) => {
      const holeCanvasPoints = getCanvasCoordinates(hole.points);
      renderShapeAnchors(
        hole.shape_type,
        holeCanvasPoints,
        color,
        annotationIndex,
        holeIndex
      );
    });

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
    const anchorId =
      holeIndex !== null
        ? `anchor-${annotationIndex}-hole-${holeIndex}-${pointIndex}`
        : `anchor-${annotationIndex}-${pointIndex}`;

    const anchor = new Konva.Circle({
      x,
      y,
      radius: 6,
      fill: "white",
      stroke: color,
      strokeWidth: 2,
      draggable: true,
      name: "anchor-point",
      id: anchorId,
    });

    // Change cursor on hover
    anchor.on("mouseenter", () => {
      const stage = anchor.getStage();
      if (stage) {
        stage.container().style.cursor = "move";
      }
      anchor.radius(8); // Make slightly larger on hover
      layer?.batchDraw();
    });

    anchor.on("mouseleave", () => {
      if (!draggingPoint.value) {
        const stage = anchor.getStage();
        if (stage) {
          stage.container().style.cursor = "default";
        }
        anchor.radius(6);
        layer?.batchDraw();
      }
    });

    // Handle dragging
    anchor.on("dragstart", () => {
      draggingPoint.value = { annotationIndex, pointIndex, holeIndex };
    });

    anchor.on("dragmove", () => {
      if (draggingPoint.value) {
        const constrainedPosition = constrainPointToParentShape(
          annotationIndex,
          anchor.position(),
          holeIndex
        );

        if (
          constrainedPosition.x !== anchor.x() ||
          constrainedPosition.y !== anchor.y()
        ) {
          anchor.position(constrainedPosition);
        }

        updateAnnotationFromDrag(
          annotationIndex,
          pointIndex,
          constrainedPosition,
          holeIndex
        );
        layer?.batchDraw();
      }
    });

    anchor.on("dragend", () => {
      if (draggingPoint.value) {
        finalizeAnnotationEdit(annotationIndex);
        draggingPoint.value = null;
        const stage = anchor.getStage();
        if (stage) {
          stage.container().style.cursor = "default";
        }
      }
    });

    layer?.add(anchor);
  };

  const removeAnchorPoints = () => {
    if (!layer) return;
    layer.find(".anchor-point").forEach((anchor) => anchor.destroy());
    layer.find(".edge-handle").forEach((edge) => edge.destroy());
    layer.find(".parent-boundary-guide").forEach((guide) => guide.destroy());
    layer.batchDraw();
  };

  const renderEdgeHandles = (
    annotationIndex: number,
    canvasPoints: number[][],
    color: string,
    holeIndex: number | null
  ) => {
    if (!layer) return;

    // Create edge handles between consecutive points
    for (let i = 0; i < canvasPoints.length; i++) {
      const startPoint = canvasPoints[i];
      const endPoint = canvasPoints[(i + 1) % canvasPoints.length]; // Wrap around to first point

      const edgeId =
        holeIndex !== null
          ? `edge-${annotationIndex}-hole-${holeIndex}-${i}`
          : `edge-${annotationIndex}-${i}`;

      // Create an invisible/semi-transparent line that's easier to click
      const edgeLine = new Konva.Line({
        points: [startPoint[0], startPoint[1], endPoint[0], endPoint[1]],
        stroke: color,
        strokeWidth: 16, // Thicker for easier clicking
        opacity: 0, // Invisible by default
        lineCap: "round",
        lineJoin: "round",
        name: "edge-handle",
        id: edgeId,
      });

      // Hover effects
      edgeLine.on("mouseenter", () => {
        const stage = edgeLine.getStage();
        if (stage) {
          stage.container().style.cursor = "copy"; // Indicate insertion
        }
        edgeLine.opacity(0.3); // Make visible on hover
        edgeLine.strokeWidth(4);
        layer?.batchDraw();
      });

      edgeLine.on("mouseleave", () => {
        const stage = edgeLine.getStage();
        if (stage) {
          stage.container().style.cursor = "default";
        }
        edgeLine.opacity(0);
        edgeLine.strokeWidth(16);
        layer?.batchDraw();
      });

      // Click to insert point
      edgeLine.on("click", () => {
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

  const getParentShapeNode = (annotationIndex: number): Konva.Shape | null => {
    return getParentShapeNodeUtil(layer, annotationIndex);
  };

  const constrainPointToParentShape = (
    annotationIndex: number,
    stagePoint: Konva.Vector2d,
    holeIndex: number | null
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
      const parentBounds = getParentShapeBounds(annotation.points);
      const clampedImagePoint = clampToParentBounds(
        getImageCoordinates([[stagePoint.x, stagePoint.y]])[0],
        parentBounds
      );
      const [canvasX, canvasY] = getCanvasCoordinates([clampedImagePoint])[0];
      return { x: canvasX, y: canvasY };
    }

    if (annotation.shape_type === "polygon") {
      const parentShape = getParentShapeNode(annotationIndex);
      if (parentShape && parentShape.intersects(stagePoint)) {
        return stagePoint;
      }

      const polygonCanvasPoints = getCanvasCoordinates(annotation.points).map(
        ([x, y]) => ({ x, y })
      );
      return getClosestPointOnPolygon(stagePoint, polygonCanvasPoints);
    }

    return stagePoint;
  };

  const insertPointOnEdge = (
    annotationIndex: number,
    edgeIndex: number,
    position: { x: number; y: number },
    holeIndex: number | null
  ) => {
    const annotation = annotations.value[annotationIndex];
    if (!annotation) return;

    const constrainedPos = constrainPointToParentShape(
      annotationIndex,
      position,
      holeIndex
    );

    // Convert canvas position to image coordinates
    const imageCoords = getImageCoordinates([
      [constrainedPos.x, constrainedPos.y],
    ])[0];

    if (holeIndex !== null) {
      // Insert point into hole - clamp to parent bounds
      const hole = annotation.holes?.[holeIndex];
      if (hole && hole.shape_type === "polygon") {
        hole.points.splice(edgeIndex + 1, 0, imageCoords);
      }
    } else if (annotation.shape_type === "polygon") {
      // Insert point into parent shape
      annotation.points.splice(edgeIndex + 1, 0, imageCoords);
    }

    updateAnswer();
    renderAnchorPoints(annotationIndex);
    updateAnnotationShape(annotationIndex);
  };

  // updateRectanglePoint is imported from konvaShapeUtils.ts

  const updateAnnotationFromDrag = (
    annotationIndex: number,
    pointIndex: number,
    newPos: { x: number; y: number },
    holeIndex: number | null
  ) => {
    const annotation = annotations.value[annotationIndex];
    if (!annotation) return;

    const imageCoords = getImageCoordinates([[newPos.x, newPos.y]])[0];
    const target =
      holeIndex !== null ? annotation.holes?.[holeIndex] : annotation;
    if (!target) return;

    if (target.shape_type === "rectangle") {
      target.points = updateRectanglePoint(
        target.points,
        pointIndex,
        imageCoords
      );
    } else if (target.shape_type === "polygon") {
      target.points[pointIndex] = imageCoords;
    }

    updateAnnotationShape(annotationIndex);
  };

  // updateKonvaShape is imported from konvaShapeUtils.ts

  const updateAnnotationShape = (annotationIndex: number) => {
    if (!layer) return;

    const { element, parentShape } = getAnnotationNodes(annotationIndex);
    if (!element || !parentShape) return;

    const annotation = annotations.value[annotationIndex];

    // Update parent shape
    updateKonvaShape(
      parentShape,
      annotation.shape_type,
      getCanvasCoordinates(annotation.points)
    );

    // Update hole shapes if they exist
    if (element instanceof Konva.Group && annotation.holes) {
      annotation.holes.forEach((hole, holeIndex) => {
        const holeShape = element.findOne(
          `#annotation-${annotationIndex}-hole-${holeIndex}`
        );
        if (holeShape) {
          updateKonvaShape(
            holeShape as Konva.Shape,
            hole.shape_type,
            getCanvasCoordinates(hole.points)
          );
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

  // createPointCircle is imported from konvaShapeUtils.ts - wrap it to handle default color
  const createPointCircleLocal = (
    x: number,
    y: number,
    color?: string
  ): Konva.Circle => {
    return createPointCircle(
      x,
      y,
      color || selectedLabel.value?.color || "#cccccc"
    );
  };

  const completePolygon = () => {
    if (mode.value.kind !== "draw-poly" && mode.value.kind !== "draw-hole-poly")
      return;
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

      // Clamp hole coordinates to parent bounds
      const parentBounds = getParentShapeBounds(parent.points);
      const clampedCoords = imageCoords.map((point) =>
        clampToParentBounds(point, parentBounds)
      );

      if (!parent.holes) {
        parent.holes = [];
      }

      parent.holes.push({
        points: clampedCoords,
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

    // Remove circles and preview line from polygon drawing mode
    if (
      mode.value.kind === "draw-poly" ||
      mode.value.kind === "draw-hole-poly"
    ) {
      mode.value.circles.forEach((circle) => circle.destroy());
      mode.value.previewLine?.destroy();
    }
  };

  const isPointWithinParent = (
    point: { x: number; y: number },
    parentIndex: number
  ): boolean => {
    const parent = annotations.value[parentIndex];
    if (!parent) return false;

    const canvasPoints = getCanvasCoordinates(parent.points);
    return checkPointWithinParent(point, canvasPoints);
  };

  // Helper to start rectangle drawing
  const startRectangleDrawing = (
    pos: { x: number; y: number },
    color: string,
    isHole: boolean,
    parentIndex?: number
  ) => {
    mode.value = isHole
      ? { kind: "draw-hole-rect", parentIndex: parentIndex!, start: pos, color }
      : { kind: "draw-rect", start: pos, color };

    drawingShape = new Konva.Rect({
      x: pos.x,
      y: pos.y,
      width: 0,
      height: 0,
      stroke: color,
      strokeWidth: 2,
      dash: [5, 5],
    });
    layer?.add(drawingShape);
    layer?.batchDraw();
  };

  // Helper to start polygon drawing
  const startPolygonDrawing = (
    pos: { x: number; y: number },
    color: string,
    isHole: boolean,
    parentIndex?: number
  ) => {
    const circle = createPointCircleLocal(pos.x, pos.y, color);
    const previewLine = new Konva.Line({
      points: [pos.x, pos.y, pos.x, pos.y],
      stroke: color,
      strokeWidth: 2,
      dash: [5, 5],
    });
    layer?.add(previewLine);

    mode.value = isHole
      ? {
          kind: "draw-hole-poly",
          parentIndex: parentIndex!,
          color,
          points: [pos.x, pos.y],
          circles: [circle],
          previewLine,
        }
      : {
          kind: "draw-poly",
          color,
          points: [pos.x, pos.y],
          circles: [circle],
          previewLine,
        };

    drawingShape = new Konva.Line({
      points: [pos.x, pos.y],
      stroke: color,
      strokeWidth: 2,
      fill: color,
      opacity: 0.3,
      closed: false,
    });
    layer?.add(drawingShape);
    layer?.add(circle);
    layer?.batchDraw();
  };

  // Helper to handle polygon point addition
  const addPolygonPoint = (pos: { x: number; y: number }, color: string) => {
    if (mode.value.kind !== "draw-poly" && mode.value.kind !== "draw-hole-poly")
      return;

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
    const circle = createPointCircleLocal(pos.x, pos.y, color);
    mode.value.circles.push(circle);
    layer?.add(circle);
    layer?.batchDraw();
  };

  const handleMouseDown = () => {
    const pos = stage?.getPointerPosition();
    if (!pos) return;

    switch (mode.value.kind) {
      case "idle": {
        const inHoleMode = sharedState.holeDrawingMode.value.active;
        const parentIndex = sharedState.holeDrawingMode.value.parentIndex;

        if (inHoleMode && parentIndex !== null) {
          if (!isPointWithinParent(pos, parentIndex)) return;

          const drawColor = getAnnotationColor(
            annotations.value[parentIndex].label
          );

          if (selectedTool.value === "rectangle") {
            startRectangleDrawing(pos, drawColor, true, parentIndex);
          } else if (selectedTool.value === "polygon") {
            startPolygonDrawing(pos, drawColor, true, parentIndex);
          }
        } else {
          if (!selectedLabel.value) {
            alert("Please select a label first");
            return;
          }

          const drawColor = selectedLabel.value.color || "#cccccc";

          if (selectedTool.value === "rectangle") {
            startRectangleDrawing(pos, drawColor, false);
          } else if (selectedTool.value === "polygon") {
            startPolygonDrawing(pos, drawColor, false);
          }
        }
        break;
      }

      case "draw-poly":
      case "draw-hole-poly": {
        addPolygonPoint(pos, mode.value.color);
        break;
      }

      case "edit":
      case "draw-rect":
      case "draw-hole-rect":
        // These modes don't handle additional clicks
        break;
    }
  };

  const handleMouseMove = () => {
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
            const firstPoint = {
              x: mode.value.points[0],
              y: mode.value.points[1],
            };
            const distance = Math.sqrt(
              Math.pow(pos.x - firstPoint.x, 2) +
                Math.pow(pos.y - firstPoint.y, 2)
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

  const handleMouseUp = () => {
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
          return;
        }

        // Convert to image coordinates
        const imageCoords = getImageCoordinates([
          [mode.value.start.x, mode.value.start.y],
          [pos.x, pos.y],
        ]);

        // Clamp hole coordinates to parent bounds
        const parent = annotations.value[mode.value.parentIndex];
        const parentBounds = getParentShapeBounds(parent.points);
        const clampedCoords = imageCoords.map((point) =>
          clampToParentBounds(point, parentBounds)
        );

        // Create hole and add to parent
        if (!parent.holes) {
          parent.holes = [];
        }

        parent.holes.push({
          points: clampedCoords,
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
        } else if (e.key === "Enter" && mode.value.points.length >= 6) {
          e.preventDefault();
          completePolygon();
        }
        break;

      case "draw-hole-rect":
        if (e.key === "Escape") {
          e.preventDefault();
          exitHoleDrawingMode();
        }
        break;

      case "edit":
        if (e.key === "Escape") {
          e.preventDefault();
          exitEditMode();
        } else if (e.key === "ArrowRight" || e.key.toLowerCase() === "n") {
          e.preventDefault();
          editNextAnnotation();
        } else if (e.key === "ArrowLeft" || e.key.toLowerCase() === "p") {
          e.preventDefault();
          editPreviousAnnotation();
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
        }
        break;

      case "draw-poly":
        if (e.key === "Escape") {
          e.preventDefault();
          cancelPolygon();
        } else if (e.key === "Enter" && mode.value.points.length >= 6) {
          e.preventDefault();
          completePolygon();
        }
        break;

      case "idle":
        // Exit hole drawing mode if active
        if (e.key === "Escape" && sharedState.holeDrawingMode.value.active) {
          e.preventDefault();
          exitHoleDrawingMode();
        }
        break;

      case "draw-rect":
        // No keyboard shortcuts in this mode
        break;
    }
  };

  const getImageCoordinates = (canvasPoints: number[][]): number[][] => {
    return getImageCoords(canvasPoints, imageNode);
  };

  const getCanvasCoordinates = (imagePoints: number[][]): number[][] => {
    return getCanvasCoords(imagePoints, imageNode);
  };

  // Helper to attach context menu handler to a Konva element
  const attachContextMenuHandler = (
    element: Konva.Node,
    annotationIndex: number,
    holeIndex?: number
  ) => {
    element.on("contextmenu", (e) => {
      e.evt.preventDefault();
      if (holeIndex !== undefined) {
        e.cancelBubble = true; // Prevent parent group from handling
      }
      const stage = element.getStage();
      if (stage) {
        const pointerPos = stage.getPointerPosition();
        if (pointerPos) {
          const container = stage.container();
          const rect = container.getBoundingClientRect();
          showContextMenu(
            annotationIndex,
            rect.left + pointerPos.x,
            rect.top + pointerPos.y,
            holeIndex
          );
        }
      }
    });
  };

  // Helper to attach hover handlers to a Konva element
  const attachHoverHandlers = (
    element: Konva.Node,
    annotationIndex: number
  ) => {
    element.on("mouseenter", () => hoverAnnotation(annotationIndex));
    element.on("mouseleave", () => unhoverAnnotation());
  };

  // Helper to render annotation with holes
  const renderAnnotationWithHoles = (
    annotation: ImageAnnotationAnswer,
    index: number,
    color: string,
    canvasPoints: number[][]
  ) => {
    const group = new Konva.Group({
      id: `annotation-${index}`,
      name: "annotation-group",
    });

    // Create parent shape
    const parentShape = createShape(
      annotation.shape_type,
      canvasPoints,
      color,
      index,
      true
    );
    if (parentShape) {
      group.add(parentShape);
    }

    // Render holes as cutouts
    annotation.holes!.forEach((hole, holeIndex) => {
      const holeCanvasPoints = getCanvasCoordinates(hole.points);
      const holeShape = createShape(
        hole.shape_type,
        holeCanvasPoints,
        color,
        index,
        false,
        holeIndex
      );

      if (holeShape) {
        attachContextMenuHandler(holeShape, index, holeIndex);
        holeShape.globalCompositeOperation("destination-out");
        group.add(holeShape);
      }
    });

    // Attach event handlers to group
    attachHoverHandlers(group, index);
    attachContextMenuHandler(group, index);

    layer?.add(group);
  };

  // Helper to render simple annotation (no holes)
  const renderSimpleAnnotation = (
    annotation: ImageAnnotationAnswer,
    index: number,
    color: string,
    canvasPoints: number[][]
  ) => {
    const shape = createShape(
      annotation.shape_type,
      canvasPoints,
      color,
      index,
      true
    );

    if (shape) {
      attachHoverHandlers(shape, index);
      attachContextMenuHandler(shape, index);
      layer?.add(shape);
    }
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
      const hasHoles = annotation.holes && annotation.holes.length > 0;

      if (hasHoles) {
        renderAnnotationWithHoles(annotation, index, color, canvasPoints);
      } else {
        renderSimpleAnnotation(annotation, index, color, canvasPoints);
      }
    });

    layer.batchDraw();
  };

  // createShape is imported from konvaShapeUtils.ts

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
  watch(sharedState.cancelPolygonTrigger, () => {
    if (
      mode.value.kind === "draw-poly" ||
      mode.value.kind === "draw-hole-poly"
    ) {
      cancelPolygon();
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
    document.addEventListener("click", hideContextMenu);
  });

  onUnmounted(() => {
    window.removeEventListener("keydown", handleKeyDown);
    clearInterval(toolPollInterval);
    if (resizeTimeout) clearTimeout(resizeTimeout);
    if (resizeObserver) resizeObserver.disconnect();
    document.removeEventListener("click", hideContextMenu);
    stage?.destroy();
  });

  return {
    canvasContainer,
    imageLoaded,
    hasError,
    contextMenu,
    editMode,
    holeDrawingMode: computed(() => sharedState.holeDrawingMode.value),
    deleteShape,
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
