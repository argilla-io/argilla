import { ref, computed, onMounted, watch, onUnmounted, type Ref } from "vue-demi";
import Konva from "konva";
import { Question } from "~/v1/domain/entities/question/Question";
import { ImageAnnotationQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";
import { ImageAnnotationAnswer } from "~/v1/domain/entities/IAnswer";

type Tool = "select" | "rectangle" | "polygon";

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
  const contextMenu = ref<{ visible: boolean; x: number; y: number; annotationIndex: number | null }>({
    visible: false,
    x: 0,
    y: 0,
    annotationIndex: null,
  });
  const draggingPoint = ref<{ annotationIndex: number; pointIndex: number } | null>(null);
  const editMode = ref<{ active: boolean; annotationIndex: number | null }>({
    active: false,
    annotationIndex: null,
  });

  let stage: Konva.Stage | null = null;
  let layer: Konva.Layer | null = null;
  let imageNode: Konva.Image | null = null;
  let drawingShape: Konva.Rect | Konva.Line | null = null;
  let isDrawing = false;
  let startPos = { x: 0, y: 0 };
  let polygonPoints: number[] = [];
  let polygonPointCircles: Konva.Circle[] = [];
  let polygonPreviewLine: Konva.Line | null = null;
  let isDrawingPolygon = false;
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
  };

  const ensureSharedState = (target: ImageAnnotationQuestionAnswer): SharedState => {
    const answerTarget = target as any;
    if (!answerTarget.__imageAnnotationSync) {
      const syncState: SharedState = {
        editModeActive: ref(false),
        currentAnnotationIndex: ref<number | null>(null),
        reassignLabel: ref(null),
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

  const highlightAnnotation = (index: number, highlight: boolean) => {
    const shape = layer?.findOne(`#annotation-${index}`);
    if (shape) {
      const isEditing = editMode.value.active && editMode.value.annotationIndex === index;
      
      if (isEditing) {
        // Editing mode: thicker stroke + glow effect + semi-transparent
        (shape as any).strokeWidth(4);
        (shape as any).shadowColor(getAnnotationColor(annotations.value[index].label));
        (shape as any).shadowBlur(8);
        (shape as any).shadowOpacity(0.8);
        (shape as any).opacity(0.5); // Semi-transparent to see through
      } else {
        // Normal hover or no hover
        (shape as any).strokeWidth(highlight ? 4 : 2);
        (shape as any).shadowBlur(0);
      }
      
      const stage = (shape as any).getStage();
      if (stage && !editMode.value.active) {
        stage.container().style.cursor = highlight ? 'pointer' : 'default';
      }
      layer?.batchDraw();
    }
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

  const showContextMenu = (index: number, x: number, y: number) => {
    contextMenu.value = {
      visible: true,
      x,
      y,
      annotationIndex: index,
    };
  };

  const enterEditMode = (annotationIndex: number) => {
    // Cancel any ongoing drawing
    if (isDrawingPolygon) {
      cancelPolygon();
    }

    editMode.value = {
      active: true,
      annotationIndex,
    };
    sharedState.editModeActive.value = true;
    sharedState.currentAnnotationIndex.value = annotationIndex;

    // Broadcast edit mode state to question component
    (answer as any).editModeState = true;
    
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

    editMode.value = {
      active: false,
      annotationIndex: null,
    };
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
    contextMenu.value.visible = false;
    contextMenu.value.annotationIndex = null;
  };

  const deleteAnnotation = (index: number) => {
    answer.values.splice(index, 1);
    renderAnnotations();
    updateAnswer();
  };

  const handleContextMenuDelete = () => {
    if (contextMenu.value.annotationIndex !== null) {
      deleteAnnotation(contextMenu.value.annotationIndex);
      hideContextMenu();
    }
  };

  const handleContextMenuEdit = () => {
    if (contextMenu.value.annotationIndex !== null) {
      enterEditMode(contextMenu.value.annotationIndex);
    }
  };

  const fadeNonEditedAnnotations = (editingIndex: number) => {
    if (!layer) return;
    
    annotations.value.forEach((_, index) => {
      if (index !== editingIndex) {
        const shape = layer?.findOne(`#annotation-${index}`);
        if (shape) {
          (shape as any).opacity(0.2); // More faded for non-edited annotations
        }
      }
    });
    
    layer.batchDraw();
  };

  const restoreAllAnnotations = () => {
    if (!layer) return;
    
    annotations.value.forEach((_, index) => {
      const shape = layer?.findOne(`#annotation-${index}`);
      if (shape) {
        (shape as any).opacity(0.3); // Restore to default opacity
      }
    });
    
    layer.batchDraw();
  };

  const renderAnchorPoints = (annotationIndex: number) => {
    if (!layer) return;
    
    // Remove existing anchor points
    removeAnchorPoints();
    
    const annotation = annotations.value[annotationIndex];
    if (!annotation) return;
    
    const color = getAnnotationColor(annotation.label);
    const canvasPoints = getCanvasCoordinates(annotation.points);
    
    // Create anchor points based on shape type
    if (annotation.shape_type === "rectangle" && canvasPoints.length === 2) {
      // For rectangles, show 4 corner points
      const [p1, p2] = canvasPoints;
      const corners = [
        { x: p1[0], y: p1[1] }, // top-left
        { x: p2[0], y: p1[1] }, // top-right
        { x: p2[0], y: p2[1] }, // bottom-right
        { x: p1[0], y: p2[1] }, // bottom-left
      ];
      
      corners.forEach((corner, pointIndex) => {
        createAnchorPoint(corner.x, corner.y, color, annotationIndex, pointIndex);
      });
    } else if (annotation.shape_type === "polygon") {
      // For polygons, render edge handles first (lower z-index)
      renderEdgeHandles(annotationIndex, canvasPoints, color);
      
      // Then show all vertex points (higher z-index)
      canvasPoints.forEach((point, pointIndex) => {
        createAnchorPoint(point[0], point[1], color, annotationIndex, pointIndex);
      });
    }
    
    layer.batchDraw();
  };

  const createAnchorPoint = (x: number, y: number, color: string, annotationIndex: number, pointIndex: number) => {
    const anchor = new Konva.Circle({
      x,
      y,
      radius: 6,
      fill: 'white',
      stroke: color,
      strokeWidth: 2,
      draggable: true,
      name: 'anchor-point',
      id: `anchor-${annotationIndex}-${pointIndex}`,
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
      draggingPoint.value = { annotationIndex, pointIndex };
    });
    
    anchor.on('dragmove', () => {
      if (draggingPoint.value) {
        updateAnnotationFromDrag(annotationIndex, pointIndex, anchor.position());
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
    layer.batchDraw();
  };

  const renderEdgeHandles = (annotationIndex: number, canvasPoints: number[][], color: string) => {
    if (!layer) return;
    
    // Create edge handles between consecutive points
    for (let i = 0; i < canvasPoints.length; i++) {
      const startPoint = canvasPoints[i];
      const endPoint = canvasPoints[(i + 1) % canvasPoints.length]; // Wrap around to first point
      
      // Create an invisible/semi-transparent line that's easier to click
      const edgeLine = new Konva.Line({
        points: [startPoint[0], startPoint[1], endPoint[0], endPoint[1]],
        stroke: color,
        strokeWidth: 16, // Thicker for easier clicking
        opacity: 0, // Invisible by default
        lineCap: 'round',
        lineJoin: 'round',
        name: 'edge-handle',
        id: `edge-${annotationIndex}-${i}`,
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
        insertPointOnEdge(annotationIndex, i, pointerPos);
      });
      
      layer.add(edgeLine);
    }
  };

  const insertPointOnEdge = (annotationIndex: number, edgeIndex: number, position: { x: number; y: number }) => {
    const annotation = annotations.value[annotationIndex];
    if (!annotation || annotation.shape_type !== "polygon") return;
    
    // Convert canvas position to image coordinates
    const imageCoords = getImageCoordinates([[position.x, position.y]])[0];
    
    // Insert the new point after the edge's start point
    annotation.points.splice(edgeIndex + 1, 0, imageCoords);
    
    // Update the answer
    updateAnswer();
    
    // Re-render anchor points to show the new point
    renderAnchorPoints(annotationIndex);
    
    // Update the annotation shape
    updateAnnotationShape(annotationIndex);
  };

  const updateAnnotationFromDrag = (annotationIndex: number, pointIndex: number, newPos: { x: number; y: number }) => {
    const annotation = annotations.value[annotationIndex];
    if (!annotation) return;
    
    if (annotation.shape_type === "rectangle") {
      // For rectangles, update the appropriate corners
      const imageCoords = getImageCoordinates([[newPos.x, newPos.y]])[0];
      
      // Rectangle has 2 points: [top-left, bottom-right]
      // pointIndex: 0=top-left, 1=top-right, 2=bottom-right, 3=bottom-left
      const currentPoints = annotation.points;
      
      if (pointIndex === 0) {
        // Top-left corner
        annotation.points = [imageCoords, currentPoints[1]];
      } else if (pointIndex === 1) {
        // Top-right corner
        annotation.points = [[currentPoints[0][0], imageCoords[1]], [imageCoords[0], currentPoints[1][1]]];
      } else if (pointIndex === 2) {
        // Bottom-right corner
        annotation.points = [currentPoints[0], imageCoords];
      } else if (pointIndex === 3) {
        // Bottom-left corner
        annotation.points = [[imageCoords[0], currentPoints[0][1]], [currentPoints[1][0], imageCoords[1]]];
      }
    } else if (annotation.shape_type === "polygon") {
      // For polygons, update the specific vertex
      const imageCoords = getImageCoordinates([[newPos.x, newPos.y]])[0];
      annotation.points[pointIndex] = imageCoords;
    }
    
    // Re-render the annotation shape in real-time
    updateAnnotationShape(annotationIndex);
  };

  const updateAnnotationShape = (annotationIndex: number) => {
    if (!layer) return;
    
    // Find and update the annotation shape
    const shape = layer.findOne(`#annotation-${annotationIndex}`);
    if (!shape) return;
    
    const annotation = annotations.value[annotationIndex];
    const color = getAnnotationColor(annotation.label);
    const canvasPoints = getCanvasCoordinates(annotation.points);
    
    if (annotation.shape_type === "rectangle" && canvasPoints.length === 2) {
      const [p1, p2] = canvasPoints;
      (shape as Konva.Rect).x(Math.min(p1[0], p2[0]));
      (shape as Konva.Rect).y(Math.min(p1[1], p2[1]));
      (shape as Konva.Rect).width(Math.abs(p2[0] - p1[0]));
      (shape as Konva.Rect).height(Math.abs(p2[1] - p1[1]));
    } else if (annotation.shape_type === "polygon") {
      const points = canvasPoints.flat();
      (shape as Konva.Line).points(points);
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

    layer = new Konva.Layer();
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

      layer.add(imageNode);
      layer.batchDraw();

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

  const createPointCircle = (x: number, y: number): Konva.Circle => {
    return new Konva.Circle({
      x,
      y,
      radius: 5,
      fill: selectedLabel.value?.color || "#cccccc",
      stroke: "white",
      strokeWidth: 2,
    });
  };

  const completePolygon = () => {
    if (!selectedLabel.value || polygonPoints.length < 6) return;

    // Convert flat array to point pairs
    const points: number[][] = [];
    for (let i = 0; i < polygonPoints.length; i += 2) {
      points.push([polygonPoints[i], polygonPoints[i + 1]]);
    }

    // Convert to image coordinates
    const imageCoords = getImageCoordinates(points);

    // Create annotation
    const annotation: ImageAnnotationAnswer = {
      label: selectedLabel.value.value,
      points: imageCoords,
      shape_type: "polygon",
      flags: {},
    };

    answer.values.push(annotation);
    updateAnswer();

    // Clean up
    cleanupPolygonDrawing();
    renderAnnotations();
  };

  const cancelPolygon = () => {
    cleanupPolygonDrawing();
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

  const handleMouseDown = (e: Konva.KonvaEventObject<MouseEvent>) => {
    // Don't start drawing if in edit mode
    if (editMode.value.active) {
      return;
    }
    
    if (!selectedLabel.value) {
      alert("Please select a label first");
      return;
    }

    const pos = stage?.getPointerPosition();
    if (!pos) return;

    // Handle rectangle drawing
    if (selectedTool.value === "rectangle") {
      isDrawing = true;
      startPos = pos;
      
      drawingShape = new Konva.Rect({
        x: pos.x,
        y: pos.y,
        width: 0,
        height: 0,
        stroke: selectedLabel.value.color,
        strokeWidth: 2,
        dash: [5, 5],
      });
      layer?.add(drawingShape);
      layer?.batchDraw();
    }
    // Handle polygon drawing
    else if (selectedTool.value === "polygon") {
      // First point - initialize polygon
      if (polygonPoints.length === 0) {
        isDrawingPolygon = true;
        polygonPoints = [pos.x, pos.y];

        // Create the polygon line
        drawingShape = new Konva.Line({
          points: polygonPoints,
          stroke: selectedLabel.value.color,
          strokeWidth: 2,
          fill: selectedLabel.value.color,
          opacity: 0.3,
          closed: false,
        });
        layer?.add(drawingShape);

        // Add first point circle
        const circle = createPointCircle(pos.x, pos.y);
        polygonPointCircles.push(circle);
        layer?.add(circle);

        // Create preview line (follows cursor)
        polygonPreviewLine = new Konva.Line({
          points: [pos.x, pos.y, pos.x, pos.y],
          stroke: selectedLabel.value.color,
          strokeWidth: 2,
          dash: [5, 5],
        });
        layer?.add(polygonPreviewLine);
      }
      // Subsequent points
      else {
        // Check if clicking near first point (close polygon)
        const firstPoint = { x: polygonPoints[0], y: polygonPoints[1] };
        const distance = Math.sqrt(
          Math.pow(pos.x - firstPoint.x, 2) + Math.pow(pos.y - firstPoint.y, 2)
        );

        if (distance < CLOSE_THRESHOLD && polygonPoints.length >= 6) {
          // Close the polygon
          completePolygon();
          return;
        }

        // Add new point
        polygonPoints.push(pos.x, pos.y);
        (drawingShape as Konva.Line)?.points(polygonPoints);

        // Add point circle
        const circle = createPointCircle(pos.x, pos.y);
        polygonPointCircles.push(circle);
        layer?.add(circle);
      }

      layer?.batchDraw();
    }
  };

  const handleMouseMove = (e: Konva.KonvaEventObject<MouseEvent>) => {
    const pos = stage?.getPointerPosition();
    if (!pos) return;

    // Handle rectangle drawing
    if (isDrawing && selectedTool.value === "rectangle" && drawingShape) {
      const width = pos.x - startPos.x;
      const height = pos.y - startPos.y;

      (drawingShape as Konva.Rect).width(width);
      (drawingShape as Konva.Rect).height(height);

      layer?.batchDraw();
    }
    // Handle polygon preview line
    else if (selectedTool.value === "polygon" && isDrawingPolygon && polygonPreviewLine) {
      // Update preview line from last point to cursor
      const lastX = polygonPoints[polygonPoints.length - 2];
      const lastY = polygonPoints[polygonPoints.length - 1];

      polygonPreviewLine.points([lastX, lastY, pos.x, pos.y]);

      // Highlight first point if cursor is near it (and we have at least 3 points)
      if (polygonPoints.length >= 6 && polygonPointCircles.length > 0) {
        const firstPoint = { x: polygonPoints[0], y: polygonPoints[1] };
        const distance = Math.sqrt(
          Math.pow(pos.x - firstPoint.x, 2) + Math.pow(pos.y - firstPoint.y, 2)
        );

        if (distance < CLOSE_THRESHOLD) {
          // Highlight first point circle
          polygonPointCircles[0].radius(8);
          polygonPointCircles[0].fill("white");
          polygonPointCircles[0].stroke(selectedLabel.value?.color || "#cccccc");
        } else {
          // Reset first point circle
          polygonPointCircles[0].radius(5);
          polygonPointCircles[0].fill(selectedLabel.value?.color || "#cccccc");
          polygonPointCircles[0].stroke("white");
        }
      }

      layer?.batchDraw();
    }
  };

  const handleMouseUp = (e: Konva.KonvaEventObject<MouseEvent>) => {
    if (!isDrawing || selectedTool.value === "polygon") return;
    if (selectedTool.value !== "rectangle") return;

    isDrawing = false;

    const pos = stage?.getPointerPosition();
    if (!pos || !drawingShape || !selectedLabel.value) return;

    const width = pos.x - startPos.x;
    const height = pos.y - startPos.y;

    // Minimum size check
    if (Math.abs(width) < 5 || Math.abs(height) < 5) {
      drawingShape.destroy();
      drawingShape = null;
      layer?.batchDraw();
      return;
    }

    // Convert to image coordinates (relative to image)
    const imageCoords = getImageCoordinates([
      [startPos.x, startPos.y],
      [pos.x, pos.y],
    ]);

    // Create annotation in labelme format
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
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    // Handle edit mode shortcuts
    if (editMode.value.active) {
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
        if (editMode.value.annotationIndex !== null) {
          const indexToDelete = editMode.value.annotationIndex;
          // Move to next annotation or exit if this was the last one
          if (annotations.value.length > 1) {
            editNextAnnotation();
          } else {
            exitEditMode();
          }
          deleteAnnotation(indexToDelete);
        }
        return;
      }
    }
    
    // Handle polygon drawing shortcuts
    if (selectedTool.value === "polygon" && isDrawingPolygon) {
      if (e.key === "Escape") {
        // Cancel polygon drawing
        e.preventDefault();
        cancelPolygon();
      } else if (e.key === "Enter" && polygonPoints.length >= 6) {
        // Force complete polygon
        e.preventDefault();
        completePolygon();
      }
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

    // Remove existing annotation shapes
    layer.find(".annotation-shape").forEach((shape) => shape.destroy());

    // Render each annotation
    annotations.value.forEach((annotation, index) => {
      const color = getAnnotationColor(annotation.label);
      const canvasPoints = getCanvasCoordinates(annotation.points);

      let shape: Konva.Rect | Konva.Line | null = null;

      if (annotation.shape_type === "rectangle" && canvasPoints.length === 2) {
        const [p1, p2] = canvasPoints;
        shape = new Konva.Rect({
          id: `annotation-${index}`,
          name: "annotation-shape",
          x: Math.min(p1[0], p2[0]),
          y: Math.min(p1[1], p2[1]),
          width: Math.abs(p2[0] - p1[0]),
          height: Math.abs(p2[1] - p1[1]),
          stroke: color,
          strokeWidth: 2,
          fill: color,
          opacity: 0.3,
          listening: true, // Enable interaction
        });
      } else if (annotation.shape_type === "polygon") {
        const points = canvasPoints.flat();
        shape = new Konva.Line({
          id: `annotation-${index}`,
          name: "annotation-shape",
          points: points,
          stroke: color,
          strokeWidth: 2,
          fill: color,
          opacity: 0.3,
          closed: true,
          listening: true, // Enable interaction
        });
      }

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
    });

    layer.batchDraw();
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
      if (shouldCancel && isDrawingPolygon) {
        cancelPolygon();
      }
    }
  );

  // Watch for enter edit mode signal from question component
  watch(
    () => (answer as any).enterEditMode,
    (annotationIndex) => {
      if (annotationIndex !== null && annotationIndex !== undefined) {
        enterEditMode(annotationIndex);
      }
    }
  );

  // Watch for exit edit mode signal from question component
  watch(
    () => (answer as any).exitEditMode,
    (shouldExit) => {
      if (shouldExit && editMode.value.active) {
        exitEditMode();
      }
    }
  );

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
    handleContextMenuDelete,
    handleContextMenuEdit,
    enterEditMode,
    exitEditMode,
    editNextAnnotation,
    editPreviousAnnotation,
  };
};
