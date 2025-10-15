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
 * Create a Konva shape (rectangle or polygon) for an annotation.
 *
 * @param shapeType - Type of shape ("rectangle" or "polygon")
 * @param canvasPoints - Array of [x, y] coordinate pairs in canvas space
 * @param color - Color for the shape stroke and fill
 * @param annotationIndex - Index of the annotation
 * @param isParent - Whether this is a parent shape or a hole
 * @param holeIndex - Optional index of the hole (if this is a hole shape)
 * @returns The created Konva shape or null if invalid
 */
export const createShape = (
  shapeType: string,
  canvasPoints: number[][],
  color: string,
  annotationIndex: number,
  isParent: boolean,
  holeIndex?: number
): Konva.Rect | Konva.Line | null => {
  const shapeId = isParent
    ? `annotation-${annotationIndex}`
    : `annotation-${annotationIndex}-hole-${holeIndex}`;
  const shapeName = isParent ? "annotation-shape" : "annotation-hole";

  if (shapeType === "rectangle" && canvasPoints.length === 2) {
    const [p1, p2] = canvasPoints;
    return new Konva.Rect({
      id: shapeId,
      name: shapeName,
      x: Math.min(p1[0], p2[0]),
      y: Math.min(p1[1], p2[1]),
      width: Math.abs(p2[0] - p1[0]),
      height: Math.abs(p2[1] - p1[1]),
      stroke: color,
      strokeWidth: 2,
      fill: color,
      opacity: isParent ? 0.3 : 1, // Holes are fully opaque for cutout
      listening: true,
    });
  } else if (shapeType === "polygon") {
    const points = canvasPoints.flat();
    return new Konva.Line({
      id: shapeId,
      name: shapeName,
      points,
      stroke: color,
      strokeWidth: 2,
      fill: color,
      opacity: isParent ? 0.3 : 1, // Holes are fully opaque for cutout
      closed: true,
      listening: true,
    });
  }

  return null;
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

/**
 * Create a visual point circle for polygon drawing.
 *
 * @param x - X coordinate in canvas space
 * @param y - Y coordinate in canvas space
 * @param color - Optional color for the circle
 * @param selectedLabel - Optional computed ref containing selected label with color fallback
 * @returns A Konva.Circle representing the point
 */
export const createPointCircle = (
  x: number,
  y: number,
  color?: string,
): Konva.Circle => {
  return new Konva.Circle({
    x,
    y,
    radius: 5,
    fill: color,
    stroke: "white",
    strokeWidth: 2,
  });
};

/**
 * Apply highlight styling to an annotation shape.
 *
 * @param layer - The Konva layer containing the annotations
 * @param imageLayer - The Konva image layer
 * @param index - The index of the annotation
 * @param highlight - Whether to highlight the annotation
 * @param isEditing - Whether the annotation is in edit mode
 * @param color - The color to use for the highlight
 */
export const highlightAnnotation = (
  layer: Konva.Layer | null,
  imageLayer: Konva.Layer | null,
  index: number,
  highlight: boolean,
  isEditing: boolean,
  color: string
) => {
  const { element, parentShape, holeShapes } = getAnnotationNodes(layer, index);
  if (!element || !parentShape) return;

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
  if (stage && !isEditing) {
    stage.container().style.cursor = highlight ? "pointer" : "default";
  }

  layer?.batchDraw();
  imageLayer?.batchDraw();
};