import Konva from "konva";

/**
 * Get the bounding box of a parent shape in image coordinates.
 *
 * @param parentPoints - Array of [x, y] coordinate pairs defining the parent shape
 * @returns Object with minX, maxX, minY, maxY bounds
 */
export const getParentShapeBounds = (parentPoints: number[][]) => {
  const xs = parentPoints.map((p) => p[0]);
  const ys = parentPoints.map((p) => p[1]);
  return {
    minX: Math.min(...xs),
    maxX: Math.max(...xs),
    minY: Math.min(...ys),
    maxY: Math.max(...ys),
  };
};

/**
 * Clamp a point to stay within parent shape bounds.
 *
 * @param point - [x, y] coordinate pair to clamp
 * @param parentBounds - Bounding box with minX, maxX, minY, maxY
 * @returns Clamped [x, y] coordinate pair
 */
export const clampToParentBounds = (
  point: number[],
  parentBounds: { minX: number; maxX: number; minY: number; maxY: number }
): number[] => {
  return [
    Math.max(parentBounds.minX, Math.min(parentBounds.maxX, point[0])),
    Math.max(parentBounds.minY, Math.min(parentBounds.maxY, point[1])),
  ];
};

/**
 * Find the closest point on a polygon's perimeter to a given point.
 * Uses perpendicular projection onto each edge segment.
 *
 * @param point - The point to find the closest polygon point to
 * @param polygonPoints - Array of {x, y} points defining the polygon
 * @returns The closest point on the polygon perimeter
 */
export const getClosestPointOnPolygon = (
  point: Konva.Vector2d,
  polygonPoints: { x: number; y: number }[]
): Konva.Vector2d => {
  let closestPoint: Konva.Vector2d = { x: point.x, y: point.y };
  let minDistance = Infinity;

  if (polygonPoints.length < 2) {
    return closestPoint;
  }

  for (let i = 0; i < polygonPoints.length; i++) {
    const p1 = polygonPoints[i];
    const p2 = polygonPoints[(i + 1) % polygonPoints.length];

    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;

    if (dx === 0 && dy === 0) continue;

    const t =
      ((point.x - p1.x) * dx + (point.y - p1.y) * dy) / (dx * dx + dy * dy);
    const clampedT = Math.max(0, Math.min(1, t));

    const candidate = {
      x: p1.x + clampedT * dx,
      y: p1.y + clampedT * dy,
    };

    const distance = Math.hypot(point.x - candidate.x, point.y - candidate.y);

    if (distance < minDistance) {
      minDistance = distance;
      closestPoint = candidate;
    }
  }

  return closestPoint;
};

/**
 * Check if a point is within a parent shape's bounding box.
 *
 * @param point - The point to check
 * @param canvasPoints - Array of [x, y] coordinate pairs defining the parent shape in canvas space
 * @returns True if the point is within the bounding box
 */
export const isPointWithinParent = (
  point: { x: number; y: number },
  canvasPoints: number[][]
): boolean => {
  // Get bounding box of parent
  const xs = canvasPoints.map((p) => p[0]);
  const ys = canvasPoints.map((p) => p[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);

  // Check if point is within bounding box
  return (
    point.x >= minX && point.x <= maxX && point.y >= minY && point.y <= maxY
  );
};
