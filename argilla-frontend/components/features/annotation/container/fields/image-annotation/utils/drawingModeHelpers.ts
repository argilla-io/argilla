import Konva from "konva";

/**
 * Initialize rectangle drawing mode.
 * Creates a dashed rectangle shape at the starting position.
 *
 * @param pos - Starting position {x, y}
 * @param color - Stroke color for the rectangle
 * @param layer - Konva layer to add the shape to
 * @returns The created Konva.Rect shape
 */
export const initRectDrawing = (
  pos: { x: number; y: number },
  color: string,
  layer: Konva.Layer | null
): Konva.Rect => {
  const rect = new Konva.Rect({
    x: pos.x,
    y: pos.y,
    width: 0,
    height: 0,
    stroke: color,
    strokeWidth: 2,
    dash: [5, 5],
  });
  layer?.add(rect);
  layer?.batchDraw();
  return rect;
};

/**
 * Initialize polygon drawing mode.
 * Creates the first point circle, preview line, and drawing shape.
 *
 * @param pos - Starting position {x, y}
 * @param color - Color for the polygon
 * @param layer - Konva layer to add shapes to
 * @param createCircle - Function to create point circles
 * @returns Object containing the drawing shape, first circle, and preview line
 */
export const initPolyDrawing = (
  pos: { x: number; y: number },
  color: string,
  layer: Konva.Layer | null,
  createCircle: (x: number, y: number, color: string) => Konva.Circle
): {
  drawingShape: Konva.Line;
  circle: Konva.Circle;
  previewLine: Konva.Line;
} => {
  const circle = createCircle(pos.x, pos.y, color);

  const previewLine = new Konva.Line({
    points: [pos.x, pos.y, pos.x, pos.y],
    stroke: color,
    strokeWidth: 2,
    dash: [5, 5],
  });

  const drawingShape = new Konva.Line({
    points: [pos.x, pos.y],
    stroke: color,
    strokeWidth: 2,
    fill: color,
    opacity: 0.3,
    closed: false,
  });

  layer?.add(previewLine);
  layer?.add(drawingShape);
  layer?.add(circle);
  layer?.batchDraw();

  return { drawingShape, circle, previewLine };
};

/**
 * Update rectangle drawing during mouse move.
 *
 * @param rect - The rectangle shape being drawn
 * @param start - Starting position {x, y}
 * @param current - Current mouse position {x, y}
 * @param layer - Konva layer to redraw
 */
export const updateRectangleDrawing = (
  rect: Konva.Rect,
  start: { x: number; y: number },
  current: { x: number; y: number },
  layer: Konva.Layer | null
) => {
  const width = current.x - start.x;
  const height = current.y - start.y;
  rect.width(width);
  rect.height(height);
  layer?.batchDraw();
};

/**
 * Update polygon preview line during mouse move.
 *
 * @param previewLine - The preview line to update
 * @param points - Flat array of polygon points [x1, y1, x2, y2, ...]
 * @param currentPos - Current mouse position {x, y}
 * @param circles - Array of point circles
 * @param color - Polygon color
 * @param closeThreshold - Distance threshold for highlighting first point
 * @param layer - Konva layer to redraw
 */
export const updatePolygonPreview = (
  previewLine: Konva.Line | null,
  points: number[],
  currentPos: { x: number; y: number },
  circles: Konva.Circle[],
  color: string,
  closeThreshold: number,
  layer: Konva.Layer | null
) => {
  if (!previewLine) return;

  // Update preview line from last point to cursor
  const lastX = points[points.length - 2];
  const lastY = points[points.length - 1];
  previewLine.points([lastX, lastY, currentPos.x, currentPos.y]);

  // Highlight first point if cursor is near it (and we have at least 3 points)
  if (points.length >= 6 && circles.length > 0) {
    const firstPoint = { x: points[0], y: points[1] };
    const distance = Math.hypot(
      currentPos.x - firstPoint.x,
      currentPos.y - firstPoint.y
    );

    if (distance < closeThreshold) {
      // Highlight first point circle
      circles[0].radius(8);
      circles[0].fill("white");
      circles[0].stroke(color);
    } else {
      // Reset first point circle
      circles[0].radius(5);
      circles[0].fill(color);
      circles[0].stroke("white");
    }
  }

  layer?.batchDraw();
};

/**
 * Add a point to the polygon being drawn.
 * Checks if the polygon should be closed (clicking near first point).
 *
 * @param pos - Position to add {x, y}
 * @param color - Polygon color
 * @param points - Current flat array of points [x1, y1, x2, y2, ...]
 * @param drawingShape - The polygon line shape
 * @param circles - Array of point circles
 * @param layer - Konva layer
 * @param closeThreshold - Distance threshold for closing polygon
 * @param createCircle - Function to create point circles
 * @returns Object with shouldComplete flag and updated circles array
 */
export const addPolygonPoint = (
  pos: { x: number; y: number },
  color: string,
  points: number[],
  drawingShape: Konva.Line,
  circles: Konva.Circle[],
  layer: Konva.Layer | null,
  closeThreshold: number,
  createCircle: (x: number, y: number, color: string) => Konva.Circle
): { shouldComplete: boolean; updatedCircles: Konva.Circle[] } => {
  // Check if clicking near first point (close polygon)
  const firstPoint = { x: points[0], y: points[1] };
  const distance = Math.hypot(pos.x - firstPoint.x, pos.y - firstPoint.y);

  if (distance < closeThreshold && points.length >= 6) {
    return { shouldComplete: true, updatedCircles: circles };
  }

  // Add new point
  points.push(pos.x, pos.y);
  drawingShape.points(points);

  // Add point circle
  const circle = createCircle(pos.x, pos.y, color);
  const updatedCircles = [...circles, circle];
  layer?.add(circle);
  layer?.batchDraw();

  return { shouldComplete: false, updatedCircles };
};

/**
 * Convert flat points array to coordinate pairs.
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

/**
 * Cleanup polygon drawing artifacts.
 * Destroys the drawing shape, circles, and preview line.
 *
 * @param drawingShape - The main polygon line shape
 * @param circles - Array of point circles
 * @param previewLine - The preview line showing next segment
 */
export const cleanupPolygonDrawing = (
  drawingShape: Konva.Shape | null,
  circles: Konva.Circle[],
  previewLine: Konva.Line | null
) => {
  drawingShape?.destroy();
  circles.forEach((circle) => circle.destroy());
  previewLine?.destroy();
};
