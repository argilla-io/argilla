import Konva from "konva";

/**
 * Type definition for annotation nodes in the Konva layer.
 */
export type AnnotationNodes = {
  element: Konva.Group | Konva.Shape | null;
  parentShape: Konva.Shape | null;
  holeShapes: Konva.Shape[];
};

/**
 * Get the Konva nodes associated with an annotation.
 *
 * @param layer - The Konva layer containing the annotations
 * @param index - The index of the annotation
 * @returns Object containing the element, parent shape, and hole shapes
 */
export const getAnnotationNodes = (
  layer: Konva.Layer | null,
  index: number
): AnnotationNodes => {
  const element = layer?.findOne(`#annotation-${index}`) as
    | Konva.Group
    | Konva.Shape
    | null;
  if (!element) return { element: null, parentShape: null, holeShapes: [] };

  if (element instanceof Konva.Group) {
    const parentShape = element.findOne(
      ".annotation-shape"
    ) as Konva.Shape | null;
    const holeShapes = element.find(".annotation-hole") as Konva.Shape[];
    return { element, parentShape, holeShapes };
  }
  return { element, parentShape: element as Konva.Shape, holeShapes: [] };
};

/**
 * Update a Konva shape's properties based on shape type and points.
 *
 * @param shape - The Konva shape to update
 * @param shapeType - Type of shape ("rectangle" or "polygon")
 * @param canvasPoints - Array of [x, y] coordinate pairs in canvas space
 */
export const updateKonvaShape = (
  shape: Konva.Shape,
  shapeType: string,
  canvasPoints: number[][]
) => {
  if (shapeType === "rectangle" && canvasPoints.length === 2) {
    const [p1, p2] = canvasPoints;
    (shape as Konva.Rect).x(Math.min(p1[0], p2[0]));
    (shape as Konva.Rect).y(Math.min(p1[1], p2[1]));
    (shape as Konva.Rect).width(Math.abs(p2[0] - p1[0]));
    (shape as Konva.Rect).height(Math.abs(p2[1] - p1[1]));
  } else if (shapeType === "polygon") {
    (shape as Konva.Line).points(canvasPoints.flat());
  }
};

/**
 * Update rectangle corner points based on which corner is being dragged.
 * Rectangles are stored as two diagonal corners [topLeft, bottomRight].
 *
 * @param currentPoints - Current rectangle points [[x1, y1], [x2, y2]]
 * @param pointIndex - Index of the corner being moved (0-3: TL, TR, BR, BL)
 * @param imageCoords - New coordinates for the corner in image space
 * @returns Updated rectangle points
 */
export const updateRectanglePoint = (
  currentPoints: number[][],
  pointIndex: number,
  imageCoords: number[]
): number[][] => {
  if (pointIndex === 0) {
    // Top-left corner
    return [imageCoords, currentPoints[1]];
  } else if (pointIndex === 1) {
    // Top-right corner
    return [
      [currentPoints[0][0], imageCoords[1]],
      [imageCoords[0], currentPoints[1][1]],
    ];
  } else if (pointIndex === 2) {
    // Bottom-right corner
    return [currentPoints[0], imageCoords];
  } else if (pointIndex === 3) {
    // Bottom-left corner
    return [
      [imageCoords[0], currentPoints[0][1]],
      [currentPoints[1][0], imageCoords[1]],
    ];
  }
  return currentPoints;
};
