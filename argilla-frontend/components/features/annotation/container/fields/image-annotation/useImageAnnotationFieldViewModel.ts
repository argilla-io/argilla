import { ref, computed, onMounted, watch, onUnmounted } from "vue-demi";
import Konva from "konva";
import { useImageAnnotationSharedState } from "./useImageAnnotationSharedState";
import { useContextMenu } from "./useContextMenu";
import {
  getImageCoordinates,
  getCanvasCoordinates,
} from "./utils/coordinateTransformUtils";
import {
  getParentShapeBounds,
  clampToParentBounds,
  isPointWithinParent as checkPointWithinParent,
  calculateImageScale,
  centerImage,
} from "./utils/geometryUtils";
import {
  getAnnotationNodes,
  createShape,
  highlightAnnotation as highlightAnnotationUtil,
} from "./utils/konvaShapeUtils";
import {
  flatPointsToCoordinatePairs,
} from "./utils/drawingModeHelpers";
import {
  ANNOTATION_SHORTCUTS,
  matchesKey,
} from "./utils/keyboardShortcuts";
import { AnnotationToolFactory } from "./tools/AnnotationToolFactory";
import { ToolContext } from "./tools/IAnnotationTool";
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
  const answer =
    imageAnnotationQuestion.answer as ImageAnnotationQuestionAnswer;
  const sharedState = useImageAnnotationSharedState(answer);
  const contextMenu = useContextMenu();

  let stage: Konva.Stage | null = null;
  let imageLayer: Konva.Layer | null = null;
  let annotationLayer: Konva.Layer | null = null;
  let imageNode: Konva.Image | null = null;
  let resizeTimeout: NodeJS.Timeout | null = null;
  let originalImageWidth = 0;
  let originalImageHeight = 0;
  let resizeObserver: ResizeObserver | null = null;
  let toolFactory: AnnotationToolFactory | null = null;

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

  const getToolContext = (): ToolContext => ({
    annotationLayer,
    imageLayer,
    imageNode,
    getAnnotationColor,
    getImageCoordinates: (points: number[][], _imageNode: Konva.Image | null) => 
      getImageCoordinates(points, imageNode), // Always use current imageNode
    getCanvasCoordinates: (points: number[][], _imageNode: Konva.Image | null) => 
      getCanvasCoordinates(points, imageNode), // Always use current imageNode
    updateAnswer,
    renderAnnotations,
    renderAnchorPoints,
    getToolForShape: (shapeType: string) => toolFactory?.getToolForShape(shapeType) || null,
  });

  const initializeToolFactory = () => {
    toolFactory = new AnnotationToolFactory(getToolContext());
  };

  const highlightAnnotation = (index: number, highlight: boolean) => {
    const isEditing =
      editMode.value.active && editMode.value.annotationIndex === index;
    const annotation = annotations.value[index];
    const color = getAnnotationColor(annotation.label);

    highlightAnnotationUtil(
      annotationLayer,
      imageLayer,
      index,
      highlight,
      isEditing,
      color
    );
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
    contextMenu.show(index, x, y, holeIndex);
  };

  const hideContextMenu = () => {
    contextMenu.hide();
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

    // Move edited shape to top of z-order (so it receives events first)
    const shapeNode = annotationLayer?.findOne(`#annotation-${annotationIndex}`);
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

    hideContextMenu();

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

  const handleContextMenuDelete = () => {
    if (contextMenu.state.value.annotationIndex !== null) {
      deleteShape(contextMenu.state.value.annotationIndex);
      hideContextMenu();
    }
  };

  const handleContextMenuEdit = () => {
    if (contextMenu.state.value.annotationIndex !== null) {
      enterEditMode(contextMenu.state.value.annotationIndex);
    }
  };

  const handleContextMenuAddHole = () => {
    if (contextMenu.state.value.annotationIndex !== null) {
      enterHoleDrawingMode(contextMenu.state.value.annotationIndex);
      hideContextMenu();
    }
  };

  const handleContextMenuDeleteHole = () => {
    if (
      contextMenu.state.value.annotationIndex !== null &&
      contextMenu.state.value.holeIndex !== null
    ) {
      const annotation = annotations.value[contextMenu.state.value.annotationIndex];
      if (
        annotation &&
        annotation.holes &&
        annotation.holes[contextMenu.state.value.holeIndex]
      ) {
        // Remove the hole
        annotation.holes.splice(contextMenu.state.value.holeIndex, 1);

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
          editMode.value.annotationIndex === contextMenu.state.value.annotationIndex
        ) {
          renderAnchorPoints(contextMenu.state.value.annotationIndex);
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
    const { parentShape } = getAnnotationNodes(annotationLayer, parentIndex);
    if (!parentShape) return;

    const annotation = annotations.value[parentIndex];
    const color = getAnnotationColor(annotation.label);

    (parentShape as any).strokeWidth(3);
    (parentShape as any).stroke(color);
    (parentShape as any).dash([10, 5]); // Dashed stroke to indicate hole drawing mode
    (parentShape as any).opacity(0.4);

    annotationLayer?.batchDraw();
    imageLayer?.batchDraw();
  };

  const fadeNonEditedAnnotations = (editingIndex: number) => {
    if (!annotationLayer) return;

    annotations.value.forEach((_, index) => {
      if (index !== editingIndex) {
        const { parentShape } = getAnnotationNodes(annotationLayer, index);
        if (parentShape) {
          (parentShape as any).opacity(0.2);
        }
      }
    });

    annotationLayer.batchDraw();
  };

  const restoreAllAnnotations = () => {
    if (!annotationLayer) return;

    annotations.value.forEach((_, index) => {
      const { parentShape } = getAnnotationNodes(annotationLayer, index);
      if (parentShape) {
        (parentShape as any).opacity(0.3);
      }
    });

    annotationLayer.batchDraw();
  };

  /**
   * Render a visual guide showing the parent shape boundary when editing holes
   */
  const renderParentBoundaryGuide = (
    annotationIndex: number,
    color: string
  ) => {
    if (!annotationLayer) return;

    const annotation = annotations.value[annotationIndex];
    if (!annotation) return;

    const canvasPoints = getCanvasCoordinates(annotation.points, imageNode);

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
      annotationLayer.add(boundaryShape);
      boundaryShape.moveToBottom(); // Keep it behind anchor points
    }
  };

  const renderAnchorPoints = (annotationIndex: number) => {
    if (!annotationLayer || !toolFactory) return;

    removeAnchorPoints();

    const annotation = annotations.value[annotationIndex];
    if (!annotation) return;

    const color = getAnnotationColor(annotation.label);
    const tool = toolFactory.getToolForShape(annotation.shape_type);
    if (!tool) return;

    // Show parent boundary guide if editing a hole
    if (draggingPoint.value?.holeIndex !== null) {
      renderParentBoundaryGuide(annotationIndex, color);
    }

    const anchorConfig = {
      annotationIndex,
      pointIndex: 0, // Will be overridden by tool
      holeIndex: null,
      onDragStart: (annIdx: number, ptIdx: number, holeIdx: number | null) => {
        draggingPoint.value = { annotationIndex: annIdx, pointIndex: ptIdx, holeIndex: holeIdx };
      },
      onDragMove: (annIdx: number, ptIdx: number, pos: { x: number; y: number }, holeIdx: number | null) => {
        // Constrain point if editing a hole
        let constrainedPos = pos;
        if (holeIdx !== null && toolFactory) {
          // Get the tool for the hole being dragged (not the parent)
          const holeShape = annotation.holes?.[holeIdx];
          if (holeShape) {
            const holeTool = toolFactory.getToolForShape(holeShape.shape_type);
            if (holeTool) {
              constrainedPos = holeTool.constrainPointToParentShape(annotation, pos, holeIdx);
            }
          }
        }
        updateAnnotationFromDrag(annIdx, ptIdx, constrainedPos, holeIdx);
      },
      onDragEnd: (annIdx: number) => {
        finalizeAnnotationEdit(annIdx);
        draggingPoint.value = null;
      },
      attachContextMenuHandler,
    };

    // Render parent shape anchors
    tool.renderAnchorPoints(annotation, annotationIndex, color, anchorConfig);

    annotationLayer.batchDraw();
  };

  const removeAnchorPoints = () => {
    if (!annotationLayer || !toolFactory) return;
    const tool = toolFactory.getTool("rectangle"); // Any tool will do for this common operation
    if (tool) {
      tool.removeAnchorPoints();
    }
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
    const targetShape = holeIndex !== null ? annotation.holes?.[holeIndex] : annotation;
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

    const containerWidth = canvasContainer.value.offsetWidth;
    const containerHeight = canvasContainer.value.offsetHeight || 500;

    stage = new Konva.Stage({
      container: canvasContainer.value,
      width: containerWidth,
      height: containerHeight,
    });

    imageLayer = new Konva.Layer();
    annotationLayer = new Konva.Layer();

    stage.add(imageLayer);
    stage.add(annotationLayer);

    // Initialize tool factory after layers are created
    initializeToolFactory();

    loadImage();
    setupEventHandlers();
  };

  const loadImage = () => {
    const img = new Image();
    img.crossOrigin = "anonymous";

    img.onload = () => {
      if (!stage || !annotationLayer) return;

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


  const isPointWithinParent = (
    point: { x: number; y: number },
    parentIndex: number
  ): boolean => {
    const parent = annotations.value[parentIndex];
    if (!parent) return false;

    const canvasPoints = getCanvasCoordinates(parent.points, imageNode);
    return checkPointWithinParent(point, canvasPoints);
  };

  const completePolygon = () => {
    if (mode.value.kind !== "draw-poly" && mode.value.kind !== "draw-hole-poly")
      return;
    if (!toolFactory) return;

    const tool = toolFactory.getTool("polygon");
    if (!tool) return;

    if (mode.value.kind === "draw-hole-poly") {
      // Create hole and add to parent
      const parent = annotations.value[mode.value.parentIndex];
      
      // Convert flat array to point pairs
      const points = flatPointsToCoordinatePairs(mode.value.points);
      const imageCoords = getImageCoordinates(points, imageNode);

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
      tool.cleanupDrawing(mode.value);
      renderAnnotations();

      // Stay in hole drawing mode for adding more holes
      highlightParentForHoleDrawing(mode.value.parentIndex);
    } else {
      // Normal annotation creation
      const annotation = tool.completeDrawing(
        mode.value,
        annotations.value,
        selectedLabel.value
      );

      if (annotation) {
        answer.values.push(annotation);
        updateAnswer();
        tool.cleanupDrawing(mode.value);
        renderAnnotations();
      }
    }

    mode.value = { kind: "idle" };
  };

  const cancelPolygon = () => {
    if (!toolFactory) return;
    const tool = toolFactory.getTool("polygon");
    if (tool && (mode.value.kind === "draw-poly" || mode.value.kind === "draw-hole-poly")) {
      tool.cancelDrawing(mode.value);
    }
    mode.value = { kind: "idle" };
    annotationLayer?.batchDraw();
  };

  const cleanupPolygonDrawing = () => {
    if (!toolFactory) return;
    const tool = toolFactory.getTool("polygon");
    if (tool && (mode.value.kind === "draw-poly" || mode.value.kind === "draw-hole-poly")) {
      tool.cleanupDrawing(mode.value);
    }
  };

  // Helper to start polygon drawing
  const startPolygonDrawing = (
    pos: { x: number; y: number },
    color: string,
    isHole: boolean,
    parentIndex?: number
  ) => {
    if (!toolFactory) return;
    const tool = toolFactory.getTool("polygon");
    if (!tool) return;

    const drawColor = color || selectedLabel.value?.color || "#cccccc";
    const state = tool.startDrawing(pos, drawColor, isHole, parentIndex);
    mode.value = state as any;
  };

  // Helper to handle polygon point addition
  const addPolygonPoint = (pos: { x: number; y: number }, color: string) => {
    if (mode.value.kind !== "draw-poly" && mode.value.kind !== "draw-hole-poly")
      return;
    if (!toolFactory) return;

    const tool = toolFactory.getTool("polygon");
    if (!tool || !tool.addPoint) return;

    const result = tool.addPoint(mode.value, pos);
    if (result.shouldComplete) {
      completePolygon();
      return;
    }

    mode.value = result.state as any;
  };

  // Helper to start rectangle drawing
  const startRectangleDrawing = (
    pos: { x: number; y: number },
    color: string,
    isHole: boolean,
    parentIndex?: number
  ) => {
    if (!toolFactory) return;
    const tool = toolFactory.getTool("rectangle");
    if (!tool) return;

    const state = tool.startDrawing(pos, color, isHole, parentIndex);
    mode.value = state as any;
  };


  // Handle mouse & keyboard events
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
    if (!pos || !toolFactory) return;

    switch (mode.value.kind) {
      case "draw-rect":
      case "draw-hole-rect": {
        const tool = toolFactory.getTool("rectangle");
        if (tool) {
          tool.updateDrawing(mode.value, pos);
        }
        break;
      }

      case "draw-poly":
      case "draw-hole-poly": {
        const tool = toolFactory.getTool("polygon");
        if (tool) {
          tool.updateDrawing(mode.value, pos);
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
    if (!pos || !toolFactory) return;

    // Use mode state machine for cleaner logic
    switch (mode.value.kind) {
      case "draw-rect": {
        const tool = toolFactory.getTool("rectangle");
        if (!tool) return;

        const width = pos.x - mode.value.start.x;
        const height = pos.y - mode.value.start.y;

        // Minimum size check
        if (Math.abs(width) < 5 || Math.abs(height) < 5) {
          tool.cleanupDrawing(mode.value);
          annotationLayer?.batchDraw();
          mode.value = { kind: "idle" };
          return;
        }

        // Convert to image coordinates
        const imageCoords = getImageCoordinates(
          [
            [mode.value.start.x, mode.value.start.y],
            [pos.x, pos.y],
          ],
          imageNode
        );

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
        tool.cleanupDrawing(mode.value);
        renderAnnotations();

        mode.value = { kind: "idle" };
        break;
      }

      case "draw-hole-rect": {
        const tool = toolFactory.getTool("rectangle");
        if (!tool) return;

        const width = pos.x - mode.value.start.x;
        const height = pos.y - mode.value.start.y;

        // Minimum size check
        if (Math.abs(width) < 5 || Math.abs(height) < 5) {
          tool.cleanupDrawing(mode.value);
          annotationLayer?.batchDraw();
          mode.value = { kind: "idle" };
          return;
        }

        // Convert to image coordinates
        const imageCoords = getImageCoordinates(
          [
            [mode.value.start.x, mode.value.start.y],
            [pos.x, pos.y],
          ],
          imageNode
        );

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
        tool.cleanupDrawing(mode.value);
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
        if (matchesKey(e, ANNOTATION_SHORTCUTS.CANCEL)) {
          e.preventDefault();
          cancelPolygon();
        } else if (
          matchesKey(e, ANNOTATION_SHORTCUTS.COMPLETE) &&
          mode.value.points.length >= 6
        ) {
          e.preventDefault();
          completePolygon();
        }
        break;

      case "draw-hole-rect":
        if (matchesKey(e, ANNOTATION_SHORTCUTS.CANCEL)) {
          e.preventDefault();
          exitHoleDrawingMode();
        }
        break;

      case "edit":
        if (matchesKey(e, ANNOTATION_SHORTCUTS.CANCEL)) {
          e.preventDefault();
          exitEditMode();
        } else if (matchesKey(e, ANNOTATION_SHORTCUTS.NEXT)) {
          e.preventDefault();
          editNextAnnotation();
        } else if (matchesKey(e, ANNOTATION_SHORTCUTS.PREVIOUS)) {
          e.preventDefault();
          editPreviousAnnotation();
        } else if (matchesKey(e, ANNOTATION_SHORTCUTS.DELETE)) {
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
        if (matchesKey(e, ANNOTATION_SHORTCUTS.CANCEL)) {
          e.preventDefault();
          cancelPolygon();
        } else if (
          matchesKey(e, ANNOTATION_SHORTCUTS.COMPLETE) &&
          mode.value.points.length >= 6
        ) {
          e.preventDefault();
          completePolygon();
        }
        break;

      case "idle":
        // Exit hole drawing mode if active
        if (
          matchesKey(e, ANNOTATION_SHORTCUTS.CANCEL) &&
          sharedState.holeDrawingMode.value.active
        ) {
          e.preventDefault();
          exitHoleDrawingMode();
        }
        break;

      case "draw-rect":
        // No keyboard shortcuts in this mode
        break;
    }
  };

  // Helper to attach context menu handler to a Konva element
  // TODO outsource after showContextMenu is refactored
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
      const holeCanvasPoints = getCanvasCoordinates(hole.points, imageNode);
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

    annotationLayer?.add(group);
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
      annotationLayer?.add(shape);
    }
  };

  const renderAnnotations = () => {
    if (!annotationLayer) return;

    // Remove existing annotation shapes and groups
    annotationLayer.find(".annotation-shape").forEach((shape) => shape.destroy());
    annotationLayer.find(".annotation-group").forEach((group) => group.destroy());

    // Render each annotation
    annotations.value.forEach((annotation, index) => {
      const color = getAnnotationColor(annotation.label);
      const canvasPoints = getCanvasCoordinates(annotation.points, imageNode);
      const hasHoles = annotation.holes && annotation.holes.length > 0;

      if (hasHoles) {
        renderAnnotationWithHoles(annotation, index, color, canvasPoints);
      } else {
        renderSimpleAnnotation(annotation, index, color, canvasPoints);
      }
    });

    annotationLayer.batchDraw();
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

    // Calculate scale and position for image
    const scale = calculateImageScale(
      containerWidth,
      containerHeight,
      originalImageWidth,
      originalImageHeight
    );

    const imageProps = centerImage(
      containerWidth,
      containerHeight,
      originalImageWidth,
      originalImageHeight,
      scale
    );

    // Apply image positioning
    imageNode.x(imageProps.x);
    imageNode.y(imageProps.y);
    imageNode.width(imageProps.width);
    imageNode.height(imageProps.height);

    // Re-render annotations
    renderAnnotations();

    // If in edit mode, re-render anchor points
    if (editMode.value.active && editMode.value.annotationIndex !== null) {
      renderAnchorPoints(editMode.value.annotationIndex);
    }

    annotationLayer?.batchDraw();
  };

  // TODO only watch should stay
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
    if (resizeTimeout) clearTimeout(resizeTimeout);
    if (resizeObserver) resizeObserver.disconnect();
    document.removeEventListener("click", hideContextMenu);
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
