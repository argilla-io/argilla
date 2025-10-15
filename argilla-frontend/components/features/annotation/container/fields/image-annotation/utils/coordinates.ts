import Konva from "konva";

/**
 * Converts canvas coordinates to image coordinates.
 * Takes into account the image's position, scale, and original dimensions.
 *
 * @param canvasPoints - Array of [x, y] coordinate pairs in canvas space
 * @param imageNode - The Konva.Image node containing the image
 * @returns Array of [x, y] coordinate pairs in image space
 */
export const getImageCoordinates = (
  canvasPoints: number[][],
  imageNode: Konva.Image | null
): number[][] => {
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

/**
 * Converts image coordinates to canvas coordinates.
 * Takes into account the image's position, scale, and original dimensions.
 *
 * @param imagePoints - Array of [x, y] coordinate pairs in image space
 * @param imageNode - The Konva.Image node containing the image
 * @returns Array of [x, y] coordinate pairs in canvas space
 */
export const getCanvasCoordinates = (
  imagePoints: number[][],
  imageNode: Konva.Image | null
): number[][] => {
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

/**
 * Convert flat points array to coordinate pairs.
 * Useful for converting Konva.Line points format to standard coordinate pairs.
 *
 * @param flatPoints - Flat array [x1, y1, x2, y2, ...]
 * @returns Array of coordinate pairs [[x1, y1], [x2, y2], ...]
 */
export const flatPointsToCoordinatePairs = (
  flatPoints: number[]
): number[][] => {
  const pairs: number[][] = [];
  for (let i = 0; i < flatPoints.length; i += 2) {
    pairs.push([flatPoints[i], flatPoints[i + 1]]);
  }
  return pairs;
};
