import { onMounted, onUnmounted, Ref } from "vue-demi";
import Konva from "konva";
import { calculateImageScale, centerImage } from "../utils/geometry";

export interface ResizeOptions {
  debounceMs?: number;
  onResize?: () => void;
}

/**
 * Composable for handling canvas resize with debouncing
 * Manages window resize and ResizeObserver for container changes
 */
export const useResize = (
  container: Ref<HTMLDivElement | null>,
  getStage: () => Konva.Stage | null,
  getImageNode: () => Konva.Image | null,
  getOriginalDimensions: () => { width: number; height: number },
  getAnnotationLayer: () => Konva.Layer | null,
  options: ResizeOptions = {}
) => {
  const { debounceMs = 150, onResize } = options;

  let resizeTimeout: NodeJS.Timeout | null = null;
  let resizeObserver: ResizeObserver | null = null;

  /**
   * Resize the canvas and reposition image
   */
  const resizeCanvas = () => {
    const stage = getStage();
    const imageNode = getImageNode();
    const annotationLayer = getAnnotationLayer();
    
    if (!stage || !container.value || !imageNode) return;

    // Get new container dimensions
    const containerWidth = container.value.offsetWidth;
    const containerHeight = container.value.offsetHeight;

    if (containerWidth === 0 || containerHeight === 0) return;

    // Update stage size
    stage.width(containerWidth);
    stage.height(containerHeight);

    const { width: originalWidth, height: originalHeight } = getOriginalDimensions();

    // Calculate scale and position for image
    const scale = calculateImageScale(
      containerWidth,
      containerHeight,
      originalWidth,
      originalHeight
    );

    const imageProps = centerImage(
      containerWidth,
      containerHeight,
      originalWidth,
      originalHeight,
      scale
    );

    // Apply image positioning
    imageNode.x(imageProps.x);
    imageNode.y(imageProps.y);
    imageNode.width(imageProps.width);
    imageNode.height(imageProps.height);

    // Trigger callback for re-rendering annotations
    if (onResize) {
      onResize();
    }

    annotationLayer?.batchDraw();
  };

  /**
   * Debounced resize handler
   */
  const handleResize = () => {
    if (resizeTimeout) clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      resizeCanvas();
    }, debounceMs);
  };

  /**
   * Setup resize listeners
   */
  const setupResizeListeners = () => {
    // Window resize
    window.addEventListener("resize", handleResize);

    // Container resize (e.g., from resizable bar)
    if (container.value) {
      resizeObserver = new ResizeObserver(() => {
        handleResize();
      });
      resizeObserver.observe(container.value);
    }
  };

  /**
   * Cleanup resize listeners
   */
  const cleanupResizeListeners = () => {
    window.removeEventListener("resize", handleResize);
    if (resizeTimeout) clearTimeout(resizeTimeout);
    if (resizeObserver) {
      resizeObserver.disconnect();
      resizeObserver = null;
    }
  };

  onMounted(() => {
    setupResizeListeners();
  });

  onUnmounted(() => {
    cleanupResizeListeners();
  });

  return {
    resizeCanvas,
    setupResizeListeners,
    cleanupResizeListeners,
  };
};
