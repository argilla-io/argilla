import Konva from "konva";

/**
 * Load image and create Konva.Image node
 * Returns a promise that resolves with the image node and dimensions
 */
export const loadImageNode = (
  content: string,
  stage: Konva.Stage,
  imageLayer: Konva.Layer
): Promise<{
  imageNode: Konva.Image;
  originalWidth: number;
  originalHeight: number;
}> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "anonymous";

    img.onload = () => {
      const stageWidth = stage.width();
      const stageHeight = stage.height();

      // Calculate scale to fit image in canvas
      const scale = Math.min(
        stageWidth / img.width,
        stageHeight / img.height,
        1 // Don't scale up
      );

      const imageNode = new Konva.Image({
        image: img,
        x: (stageWidth - img.width * scale) / 2,
        y: (stageHeight - img.height * scale) / 2,
        width: img.width * scale,
        height: img.height * scale,
      });

      imageLayer.add(imageNode);
      imageLayer.batchDraw();

      resolve({
        imageNode,
        originalWidth: img.width,
        originalHeight: img.height,
      });
    };

    img.onerror = () => {
      reject(new Error("Failed to load image"));
    };

    img.src = content;
  });
};
