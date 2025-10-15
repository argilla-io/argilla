import Konva from "konva";

/**
 * Initialize Konva stage with layers
 * Simple helper that creates and returns stage objects
 */
export const initKonvaStage = (
  container: HTMLDivElement,
  onMouseDown?: () => void,
  onMouseMove?: () => void,
  onMouseUp?: () => void
) => {
  const containerWidth = container.offsetWidth;
  const containerHeight = container.offsetHeight || 500;

  const stage = new Konva.Stage({
    container,
    width: containerWidth,
    height: containerHeight,
  });

  const imageLayer = new Konva.Layer();
  const annotationLayer = new Konva.Layer();

  stage.add(imageLayer);
  stage.add(annotationLayer);

  // Setup event handlers
  if (onMouseDown) {
    stage.on("mousedown touchstart", onMouseDown);
  }
  if (onMouseMove) {
    stage.on("mousemove touchmove", onMouseMove);
  }
  if (onMouseUp) {
    stage.on("mouseup touchend", onMouseUp);
  }

  return {
    stage,
    imageLayer,
    annotationLayer,
  };
};
