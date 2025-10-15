import Konva from "konva";
import { ImageAnnotationAnswer } from "~/v1/domain/entities/IAnswer";

export interface DrawingState {
  kind: string;
  color: string;
  [key: string]: any;
}

export interface ToolContext {
  annotationLayer: Konva.Layer | null;
  imageLayer: Konva.Layer | null;
  imageNode: Konva.Image | null;
  getAnnotationColor: (labelValue: string) => string;
  getImageCoordinates: (points: number[][], imageNode: Konva.Image | null) => number[][];
  getCanvasCoordinates: (points: number[][], imageNode: Konva.Image | null) => number[][];
  updateAnswer: () => void;
  renderAnnotations: () => void;
  renderAnchorPoints?: (annotationIndex: number) => void;
  getToolForShape?: (shapeType: string) => IAnnotationTool | null;
}

export interface AnchorPointConfig {
  annotationIndex: number;
  pointIndex: number;
  holeIndex: number | null;
  onDragStart?: (annotationIndex: number, pointIndex: number, holeIndex: number | null) => void;
  onDragMove?: (annotationIndex: number, pointIndex: number, position: { x: number; y: number }, holeIndex: number | null) => void;
  onDragEnd?: (annotationIndex: number) => void;
  attachContextMenuHandler?: (element: Konva.Node, annotationIndex: number, holeIndex?: number) => void;
}

/**
 * Interface for annotation tools (Rectangle, Polygon, etc.)
 * Each tool implements the complete lifecycle of drawing and editing shapes
 */
export interface IAnnotationTool {
  /**
   * The type of shape this tool creates (e.g., "rectangle", "polygon")
   */
  readonly shapeType: string;

  /**
   * Start drawing a new shape
   * @param pos - Starting position
   * @param color - Color for the shape
   * @param isHole - Whether this is a hole being drawn inside a parent shape
   * @param parentIndex - Index of parent annotation if drawing a hole
   * @returns DrawingState for tracking the drawing process
   */
  startDrawing(
    pos: { x: number; y: number },
    color: string,
    isHole: boolean,
    parentIndex?: number
  ): DrawingState;

  /**
   * Update the drawing preview as the mouse moves
   * @param state - Current drawing state
   * @param pos - Current mouse position
   */
  updateDrawing(state: DrawingState, pos: { x: number; y: number }): void;

  /**
   * Add a point to the shape (for polygon-like tools)
   * @param state - Current drawing state
   * @param pos - Position to add
   * @returns Updated state and whether drawing should complete
   */
  addPoint?(
    state: DrawingState,
    pos: { x: number; y: number }
  ): { state: DrawingState; shouldComplete: boolean };

  /**
   * Complete the drawing and create the annotation
   * @param state - Current drawing state
   * @param annotations - Array of existing annotations
   * @param selectedLabel - Currently selected label
   * @returns The created annotation or null if creation failed
   */
  completeDrawing(
    state: DrawingState,
    annotations: ImageAnnotationAnswer[],
    selectedLabel: { value: string; color: string } | undefined
  ): ImageAnnotationAnswer | null;

  /**
   * Cancel the current drawing and cleanup
   * @param state - Current drawing state
   */
  cancelDrawing(state: DrawingState): void;

  /**
   * Cleanup drawing artifacts (temporary shapes, circles, etc.)
   * @param state - Current drawing state
   */
  cleanupDrawing(state: DrawingState): void;

  /**
   * Render anchor points for editing a shape
   * @param annotation - The annotation to edit
   * @param annotationIndex - Index of the annotation
   * @param color - Color for the anchor points
   * @param config - Configuration for anchor point behavior
   */
  renderAnchorPoints(
    annotation: ImageAnnotationAnswer,
    annotationIndex: number,
    color: string,
    config: AnchorPointConfig
  ): void;

  /**
   * Create a single anchor point
   * @param x - X position
   * @param y - Y position
   * @param color - Color for the anchor point
   * @param config - Configuration for the anchor point
   */
  createAnchorPoint(
    x: number,
    y: number,
    color: string,
    config: AnchorPointConfig
  ): Konva.Circle;

  /**
   * Render edge handles for inserting new points (polygon-like tools)
   * @param annotation - The annotation
   * @param annotationIndex - Index of the annotation
   * @param canvasPoints - Points in canvas coordinates
   * @param color - Color for the handles
   * @param holeIndex - Index of hole if editing a hole
   * @param onInsertPoint - Callback when a point is inserted
   * @param attachContextMenuHandler - Optional callback to attach context menu
   */
  renderEdgeHandles?(
    annotation: ImageAnnotationAnswer,
    annotationIndex: number,
    canvasPoints: number[][],
    color: string,
    holeIndex: number | null,
    onInsertPoint: (annotationIndex: number, edgeIndex: number, position: { x: number; y: number }, holeIndex: number | null) => void,
    attachContextMenuHandler?: (element: Konva.Node, annotationIndex: number, holeIndex?: number) => void
  ): void;

  /**
   * Remove all anchor points and edge handles
   */
  removeAnchorPoints(): void;

  /**
   * Constrain a point to stay within the parent shape (for holes)
   * @param parentAnnotation - The parent annotation
   * @param stagePoint - Point to constrain
   * @param holeIndex - Index of the hole being edited
   * @returns Constrained position
   */
  constrainPointToParentShape(
    parentAnnotation: ImageAnnotationAnswer,
    stagePoint: Konva.Vector2d,
    holeIndex: number | null
  ): Konva.Vector2d;

  /**
   * Insert a new point on an edge (for polygon-like tools)
   * @param annotation - The annotation
   * @param annotationIndex - Index of the annotation
   * @param edgeIndex - Index of the edge where point should be inserted
   * @param position - Position for the new point
   * @param holeIndex - Index of hole if inserting in a hole
   */
  insertPointOnEdge?(
    annotation: ImageAnnotationAnswer,
    annotationIndex: number,
    edgeIndex: number,
    position: { x: number; y: number },
    holeIndex: number | null
  ): void;

  /**
   * Update annotation data from dragging an anchor point
   * @param annotation - The annotation to update
   * @param pointIndex - Index of the point being dragged
   * @param newPos - New position for the point
   * @param holeIndex - Index of hole if editing a hole
   */
  updateAnnotationFromDrag(
    annotation: ImageAnnotationAnswer,
    pointIndex: number,
    newPos: { x: number; y: number },
    holeIndex: number | null
  ): void;

  /**
   * Update the visual representation of the annotation shape
   * @param annotation - The annotation
   * @param annotationIndex - Index of the annotation
   */
  updateAnnotationShape(
    annotation: ImageAnnotationAnswer,
    annotationIndex: number
  ): void;
}
