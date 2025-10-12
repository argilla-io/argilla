import { ref, computed, onMounted, watch, onUnmounted } from "vue-demi";
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
  const CLOSE_THRESHOLD = 10;

  const answer = imageAnnotationQuestion.answer as ImageAnnotationQuestionAnswer;

  const annotations = computed(() => answer.values);

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
      (shape as any).strokeWidth(highlight ? 4 : 2);
      const stage = (shape as any).getStage();
      if (stage) {
        stage.container().style.cursor = highlight ? 'pointer' : 'default';
      }
      layer?.batchDraw();
    }
  };

  const hoverAnnotation = (index: number) => {
    hoveredAnnotation.value = index;
    highlightAnnotation(index, true);
  };

  const unhoverAnnotation = () => {
    if (hoveredAnnotation.value !== null) {
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

  onMounted(() => {
    initCanvas();

    // Handle window resize
    window.addEventListener("resize", () => {
      if (stage && canvasContainer.value) {
        const width = canvasContainer.value.offsetWidth;
        stage.width(width);
        renderAnnotations();
      }
    });

    // Close context menu on click outside
    document.addEventListener('click', hideContextMenu);
  });

  onUnmounted(() => {
    window.removeEventListener("keydown", handleKeyDown);
    clearInterval(toolPollInterval);
    document.removeEventListener('click', hideContextMenu);
    stage?.destroy();
  });

  return {
    canvasContainer,
    imageLoaded,
    hasError,
    contextMenu,
    handleContextMenuDelete,
  };
};
