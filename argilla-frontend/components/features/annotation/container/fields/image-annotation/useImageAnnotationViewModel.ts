import { ref, onMounted, onUnmounted, computed } from "vue-demi";
import Konva from "konva";
import { Question } from "~/v1/domain/entities/question/Question";
import { ImageAnnotationQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";
import { ImageAnnotationAnswer } from "~/v1/domain/entities/IAnswer";

type Tool = "select" | "rectangle" | "polygon";

export const useImageAnnotationViewModel = (props: {
  id: string;
  name: string;
  content: string;
  imageAnnotationQuestion: Question;
}) => {
  const { content, imageAnnotationQuestion } = props;
  
  const canvasContainer = ref<HTMLDivElement | null>(null);
  const imageLoaded = ref(false);
  const hasError = ref(false);
  const selectedTool = ref<Tool>("select");
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

  const answer = imageAnnotationQuestion.answer as ImageAnnotationQuestionAnswer;

  const annotations = computed(() => answer.values);

  const selectedLabel = computed(() => {
    return answer.options.find((opt) => opt.isSelected);
  });

  const selectTool = (tool: Tool) => {
    selectedTool.value = tool;
    // Cancel any ongoing drawing
    if (drawingShape) {
      drawingShape.destroy();
      drawingShape = null;
    }
    polygonPoints = [];
    isDrawing = false;
    layer?.batchDraw();
  };

  const selectLabel = (option: any) => {
    answer.options.forEach((opt) => {
      opt.isSelected = opt.id === option.id;
    });
  };

  const getLabelCount = (labelValue: string) => {
    return annotations.value.filter((ann) => ann.label === labelValue).length;
  };

  const getAnnotationColor = (labelValue: string) => {
    const option = answer.options.find((opt) => opt.value === labelValue);
    return option?.color || "#cccccc";
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

  const selectAnnotation = (index: number) => {
    // TODO: Enable editing mode for selected annotation
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
    stage.on("dblclick", handleDoubleClick);
  };

  const handleMouseDown = (e: Konva.KonvaEventObject<MouseEvent>) => {
    if (selectedTool.value === "select") return;
    if (!selectedLabel.value) {
      alert("Please select a label first");
      return;
    }

    const pos = stage?.getPointerPosition();
    if (!pos) return;

    isDrawing = true;
    startPos = pos;

    if (selectedTool.value === "rectangle") {
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
    } else if (selectedTool.value === "polygon") {
      if (polygonPoints.length === 0) {
        polygonPoints = [pos.x, pos.y];
        drawingShape = new Konva.Line({
          points: polygonPoints,
          stroke: selectedLabel.value.color,
          strokeWidth: 2,
          dash: [5, 5],
          closed: false,
        });
        layer?.add(drawingShape);
      } else {
        polygonPoints.push(pos.x, pos.y);
        (drawingShape as Konva.Line)?.points(polygonPoints);
      }
    }

    layer?.batchDraw();
  };

  const handleMouseMove = (e: Konva.KonvaEventObject<MouseEvent>) => {
    if (!isDrawing || selectedTool.value !== "rectangle") return;

    const pos = stage?.getPointerPosition();
    if (!pos || !drawingShape) return;

    const width = pos.x - startPos.x;
    const height = pos.y - startPos.y;

    (drawingShape as Konva.Rect).width(width);
    (drawingShape as Konva.Rect).height(height);

    layer?.batchDraw();
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

  const handleDoubleClick = () => {
    if (selectedTool.value !== "polygon" || polygonPoints.length < 6) return;
    if (!selectedLabel.value) return;

    // Convert polygon points to image coordinates
    const points: number[][] = [];
    for (let i = 0; i < polygonPoints.length; i += 2) {
      points.push([polygonPoints[i], polygonPoints[i + 1]]);
    }

    const imageCoords = getImageCoordinates(points);

    const annotation: ImageAnnotationAnswer = {
      label: selectedLabel.value.value,
      points: imageCoords,
      shape_type: "polygon",
      flags: {},
    };

    answer.values.push(annotation);
    updateAnswer();

    if (drawingShape) {
      drawingShape.destroy();
      drawingShape = null;
    }
    polygonPoints = [];
    renderAnnotations();
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
    stage?.destroy();
    document.removeEventListener('click', hideContextMenu);
  });

  return {
    canvasContainer,
    imageLoaded,
    hasError,
    selectedTool,
    hoveredAnnotation,
    annotations,
    contextMenu,
    selectTool,
    selectLabel,
    getLabelCount,
    getAnnotationColor,
    hoverAnnotation,
    unhoverAnnotation,
    selectAnnotation,
    hideContextMenu,
  };
};
