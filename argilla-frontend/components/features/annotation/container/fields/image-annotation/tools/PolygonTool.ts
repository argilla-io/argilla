import Konva from "konva";
import { flatPointsToCoordinatePairs } from "../utils/coordinates";
import {
  getParentShapeBounds,
  clampToParentBounds,
  getClosestPointOnPolygon,
  isPointWithinParent as checkPointWithinParent,
} from "../utils/geometry";
import { ANNOTATION_SHORTCUTS, matchesKey } from "../utils/keyboardShortcuts";
import { BaseAnnotationTool } from "./BaseAnnotationTool";
import { DrawingState, AnchorPointConfig } from "./IAnnotationTool";
import {
  ToolInteraction,
  InteractionContext,
  InteractionResult,
} from "./IToolInteraction";
import { ImageAnnotationAnswer } from "~/v1/domain/entities/IAnswer";

interface PolygonDrawingState extends DrawingState {
  kind: "draw-poly" | "draw-hole-poly";
  color: string;
  points: number[];
  circles: Konva.Circle[];
  previewLine: Konva.Line | null;
  parentIndex?: number;
}

/**
 * Interaction implementation for polygon drawing.
 * Encapsulates all state and behavior for drawing a polygon annotation.
 */
class PolygonInteraction implements ToolInteraction {
  readonly kind = "drawing" as const;
  readonly toolType = "polygon";
  readonly isHole: boolean;
  readonly parentIndex?: number;
  readonly color: string;

  private points: number[] = [];
  private circles: Konva.Circle[] = [];
  private previewLine: Konva.Line | null = null;
  private drawingShape: Konva.Line | null = null;
  private readonly CLOSE_THRESHOLD = 10;

  constructor(
    private context: InteractionContext,
    private selectedLabel: { value: string; color: string } | undefined,
    startPos: { x: number; y: number },
    color: string,
    isHole: boolean,
    parentIndex?: number
  ) {
    this.color = color;
    this.isHole = isHole;
    this.parentIndex = parentIndex;

    // Initialize first point
    const result = this.initPolyDrawing(startPos, color);
    this.points = [startPos.x, startPos.y];
    this.circles = [result.circle];
    this.previewLine = result.previewLine;
    this.drawingShape = result.drawingShape;
  }

  /**
   * Create a visual point circle for polygon drawing
   */
  private createPointCircle(x: number, y: number, color: string): Konva.Circle {
    return new Konva.Circle({
      x,
      y,
      radius: 5,
      fill: color,
      stroke: "white",
      strokeWidth: 2,
    });
  }

  /**
   * Initialize polygon drawing with first point
   */
  private initPolyDrawing(
    pos: { x: number; y: number },
    color: string
  ): {
    drawingShape: Konva.Line;
    circle: Konva.Circle;
    previewLine: Konva.Line;
  } {
    const circle = this.createPointCircle(pos.x, pos.y, color);

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

    this.context.annotationLayer?.add(previewLine);
    this.context.annotationLayer?.add(drawingShape);
    this.context.annotationLayer?.add(circle);
    this.context.annotationLayer?.batchDraw();

    return { drawingShape, circle, previewLine };
  }

  /**
   * Add a point to the polygon
   */
  private addPolyPoint(pos: { x: number; y: number }): {
    shouldComplete: boolean;
    updatedCircles: Konva.Circle[];
  } {
    const firstPoint = { x: this.points[0], y: this.points[1] };
    const distance = Math.hypot(pos.x - firstPoint.x, pos.y - firstPoint.y);

    if (distance < this.CLOSE_THRESHOLD && this.points.length >= 6) {
      return { shouldComplete: true, updatedCircles: this.circles };
    }

    this.points.push(pos.x, pos.y);
    (this.drawingShape as Konva.Line).points(this.points);

    const circle = this.createPointCircle(pos.x, pos.y, this.color);
    const updatedCircles = [...this.circles, circle];
    this.context.annotationLayer?.add(circle);
    this.context.annotationLayer?.batchDraw();

    return { shouldComplete: false, updatedCircles };
  }

  /**
   * Update polygon preview line
   */
  private updatePolygonPreview(pos: { x: number; y: number }): void {
    if (!this.previewLine) return;

    const lastX = this.points[this.points.length - 2];
    const lastY = this.points[this.points.length - 1];
    this.previewLine.points([lastX, lastY, pos.x, pos.y]);

    if (this.points.length >= 6 && this.circles.length > 0) {
      const firstPoint = { x: this.points[0], y: this.points[1] };
      const distance = Math.hypot(pos.x - firstPoint.x, pos.y - firstPoint.y);

      if (distance < this.CLOSE_THRESHOLD) {
        this.circles[0].radius(8);
        this.circles[0].fill("white");
        this.circles[0].stroke(this.color);
      } else {
        this.circles[0].radius(5);
        this.circles[0].fill(this.color);
        this.circles[0].stroke("white");
      }
    }

    this.context.annotationLayer?.batchDraw();
  }

  onPointerDown(pos: { x: number; y: number }): InteractionResult {
    const result = this.addPolyPoint(pos);
    this.circles = result.updatedCircles;
    return { shouldComplete: result.shouldComplete };
  }

  onPointerMove(pos: { x: number; y: number }): void {
    this.updatePolygonPreview(pos);
  }

  onPointerUp(_pos: { x: number; y: number }): InteractionResult {
    return { shouldContinue: true };
  }

  onKeyDown(e: KeyboardEvent): InteractionResult {
    if (matchesKey(e, ANNOTATION_SHORTCUTS.CANCEL)) {
      e.preventDefault();
      return { shouldCancel: true };
    }
    if (
      matchesKey(e, ANNOTATION_SHORTCUTS.COMPLETE) &&
      this.points.length >= 6
    ) {
      e.preventDefault();
      return { shouldComplete: true };
    }
    return { shouldContinue: true };
  }

  complete(): ImageAnnotationAnswer | null {
    if (this.points.length < 6) return null;

    const pointPairs = flatPointsToCoordinatePairs(this.points);
    const imageCoords = this.context.getImageCoordinates(
      pointPairs,
      this.context.imageNode
    );

    if (this.isHole) {
      // Hole creation is handled by the controller
      // Return null to signal that the controller should handle it
      return null;
    }

    if (!this.selectedLabel) return null;

    return {
      label: this.selectedLabel.value,
      points: imageCoords,
      shape_type: "polygon",
      flags: {},
    };
  }

  cancel(): void {
    this.cleanup();
  }

  cleanup(): void {
    this.drawingShape?.destroy();
    this.circles.forEach((circle) => circle.destroy());
    this.previewLine?.destroy();
    this.context.annotationLayer?.batchDraw();
  }

  /**
   * Get the current points for hole creation (used by controller)
   */
  getPoints(): number[] {
    return this.points;
  }
}

/**
 * Tool for drawing and editing polygon annotations
 */
export class PolygonTool extends BaseAnnotationTool {
  readonly shapeType = "polygon";
  private readonly CLOSE_THRESHOLD = 10;

  /**
   * Create a visual point circle for polygon drawing
   */
  private createPointCircle(x: number, y: number, color: string): Konva.Circle {
    return new Konva.Circle({
      x,
      y,
      radius: 5,
      fill: color,
      stroke: "white",
      strokeWidth: 2,
    });
  }

  /**
   * Initialize polygon drawing with first point
   */
  private initPolyDrawing(
    pos: { x: number; y: number },
    color: string
  ): {
    drawingShape: Konva.Line;
    circle: Konva.Circle;
    previewLine: Konva.Line;
  } {
    const circle = this.createPointCircle(pos.x, pos.y, color);

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

    this.context.annotationLayer?.add(previewLine);
    this.context.annotationLayer?.add(drawingShape);
    this.context.annotationLayer?.add(circle);
    this.context.annotationLayer?.batchDraw();

    return { drawingShape, circle, previewLine };
  }

  /**
   * Add a point to the polygon
   */
  private addPolyPoint(
    pos: { x: number; y: number },
    color: string,
    points: number[],
    drawingShape: Konva.Line,
    circles: Konva.Circle[]
  ): { shouldComplete: boolean; updatedCircles: Konva.Circle[] } {
    const firstPoint = { x: points[0], y: points[1] };
    const distance = Math.hypot(pos.x - firstPoint.x, pos.y - firstPoint.y);

    if (distance < this.CLOSE_THRESHOLD && points.length >= 6) {
      return { shouldComplete: true, updatedCircles: circles };
    }

    points.push(pos.x, pos.y);
    drawingShape.points(points);

    const circle = this.createPointCircle(pos.x, pos.y, color);
    const updatedCircles = [...circles, circle];
    this.context.annotationLayer?.add(circle);
    this.context.annotationLayer?.batchDraw();

    return { shouldComplete: false, updatedCircles };
  }

  /**
   * Update polygon preview line
   */
  private updatePolygonPreview(
    previewLine: Konva.Line | null,
    points: number[],
    pos: { x: number; y: number },
    circles: Konva.Circle[],
    color: string
  ): void {
    if (!previewLine) return;

    const lastX = points[points.length - 2];
    const lastY = points[points.length - 1];
    previewLine.points([lastX, lastY, pos.x, pos.y]);

    if (points.length >= 6 && circles.length > 0) {
      const firstPoint = { x: points[0], y: points[1] };
      const distance = Math.hypot(pos.x - firstPoint.x, pos.y - firstPoint.y);

      if (distance < this.CLOSE_THRESHOLD) {
        circles[0].radius(8);
        circles[0].fill("white");
        circles[0].stroke(color);
      } else {
        circles[0].radius(5);
        circles[0].fill(color);
        circles[0].stroke("white");
      }
    }

    this.context.annotationLayer?.batchDraw();
  }

  createInteraction(
    context: InteractionContext,
    startPos: { x: number; y: number },
    color: string,
    isHole: boolean,
    parentIndex?: number,
    selectedLabel?: { value: string; color: string }
  ): ToolInteraction {
    return new PolygonInteraction(
      context,
      selectedLabel,
      startPos,
      color,
      isHole,
      parentIndex
    );
  }

  startDrawing(
    pos: { x: number; y: number },
    color: string,
    isHole: boolean,
    parentIndex?: number
  ): PolygonDrawingState {
    const drawColor = color || "#cccccc";
    const result = this.initPolyDrawing(pos, drawColor);

    this.drawingShape = result.drawingShape;

    return isHole
      ? {
          kind: "draw-hole-poly",
          parentIndex: parentIndex!,
          color,
          points: [pos.x, pos.y],
          circles: [result.circle],
          previewLine: result.previewLine,
        }
      : {
          kind: "draw-poly",
          color,
          points: [pos.x, pos.y],
          circles: [result.circle],
          previewLine: result.previewLine,
        };
  }

  updateDrawing(state: DrawingState, pos: { x: number; y: number }): void {
    const polyState = state as PolygonDrawingState;
    this.updatePolygonPreview(
      polyState.previewLine,
      polyState.points,
      pos,
      polyState.circles,
      polyState.color
    );
  }

  addPoint(
    state: DrawingState,
    pos: { x: number; y: number }
  ): { state: DrawingState; shouldComplete: boolean } {
    const polyState = state as PolygonDrawingState;
    const drawColor = polyState.color || "#cccccc";

    const result = this.addPolyPoint(
      pos,
      drawColor,
      polyState.points,
      this.drawingShape as Konva.Line,
      polyState.circles
    );

    if (result.shouldComplete) {
      return { state: polyState, shouldComplete: true };
    }

    // Note: addPolyPoint already pushes the point to polyState.points array
    // We only need to update the circles reference
    polyState.circles = result.updatedCircles;
    return { state: polyState, shouldComplete: false };
  }

  completeDrawing(
    state: DrawingState,
    _annotations: ImageAnnotationAnswer[],
    selectedLabel: { value: string; color: string } | undefined
  ): ImageAnnotationAnswer | null {
    const polyState = state as PolygonDrawingState;

    if (polyState.points.length < 6) return null;

    // Convert flat array to point pairs
    const points = flatPointsToCoordinatePairs(polyState.points);

    // Convert to image coordinates
    const imageCoords = this.context.getImageCoordinates(
      points,
      this.context.imageNode
    );

    if (polyState.kind === "draw-hole-poly") {
      // Return null - hole creation is handled by the caller
      return null;
    }

    // Normal annotation creation
    if (!selectedLabel) return null;

    return {
      label: selectedLabel.value,
      points: imageCoords,
      shape_type: "polygon",
      flags: {},
    };
  }

  cancelDrawing(state: DrawingState): void {
    this.cleanupDrawing(state);
  }

  cleanupDrawing(state: DrawingState): void {
    const polyState = state as PolygonDrawingState;
    this.drawingShape?.destroy();
    polyState.circles.forEach((circle) => circle.destroy());
    polyState.previewLine?.destroy();
    if (this.drawingShape) {
      this.drawingShape = null;
    }
    this.context.annotationLayer?.batchDraw();
  }

  renderAnchorPoints(
    annotation: ImageAnnotationAnswer,
    annotationIndex: number,
    color: string,
    config: AnchorPointConfig
  ): void {
    const canvasPoints = this.context.getCanvasCoordinates(
      annotation.points,
      this.context.imageNode
    );

    // Render edge handles for inserting new points
    this.renderEdgeHandles(
      annotation,
      annotationIndex,
      canvasPoints,
      color,
      null,
      (annIdx, edgeIdx, pos, holeIdx) => {
        this.insertPointOnEdge(annotation, annIdx, edgeIdx, pos, holeIdx);
      },
      config.attachContextMenuHandler
    );

    // Render vertex anchor points
    canvasPoints.forEach((point, pointIndex) => {
      this.createAnchorPoint(point[0], point[1], color, {
        ...config,
        pointIndex,
      });
    });

    // Render hole anchors - delegate to appropriate tool based on hole shape type
    annotation.holes?.forEach((hole, holeIndex) => {
      if (hole.shape_type === "polygon") {
        // Render polygon holes directly
        const holeCanvasPoints = this.context.getCanvasCoordinates(
          hole.points,
          this.context.imageNode
        );

        // Render edge handles for hole
        this.renderEdgeHandles(
          annotation,
          annotationIndex,
          holeCanvasPoints,
          color,
          holeIndex,
          (annIdx, edgeIdx, pos, holeIdx) => {
            this.insertPointOnEdge(annotation, annIdx, edgeIdx, pos, holeIdx);
          },
          config.attachContextMenuHandler
        );

        // Render vertex anchor points for hole
        holeCanvasPoints.forEach((point, pointIndex) => {
          this.createAnchorPoint(point[0], point[1], color, {
            ...config,
            pointIndex,
            holeIndex,
          });
        });
      } else if (
        hole.shape_type === "rectangle" &&
        this.context.getToolForShape
      ) {
        // Delegate rectangle holes to RectangleTool
        const rectTool = this.context.getToolForShape("rectangle");
        if (rectTool) {
          const holeCanvasPoints = this.context.getCanvasCoordinates(
            hole.points,
            this.context.imageNode
          );
          if (holeCanvasPoints.length === 2) {
            const [hp1, hp2] = holeCanvasPoints;
            const holeCorners = [
              { x: hp1[0], y: hp1[1] },
              { x: hp2[0], y: hp1[1] },
              { x: hp2[0], y: hp2[1] },
              { x: hp1[0], y: hp2[1] },
            ];
            holeCorners.forEach((corner, pointIndex) => {
              this.createAnchorPoint(corner.x, corner.y, color, {
                ...config,
                pointIndex,
                holeIndex,
              });
            });
          }
        }
      }
    });

    this.context.annotationLayer?.batchDraw();
  }

  renderEdgeHandles(
    _annotation: ImageAnnotationAnswer,
    annotationIndex: number,
    canvasPoints: number[][],
    color: string,
    holeIndex: number | null,
    onInsertPoint: (
      annotationIndex: number,
      edgeIndex: number,
      position: { x: number; y: number },
      holeIndex: number | null
    ) => void,
    attachContextMenuHandler?: (
      element: Konva.Node,
      annotationIndex: number,
      holeIndex?: number
    ) => void
  ): void {
    if (!this.context.annotationLayer) return;

    // Create edge handles between consecutive points
    for (let i = 0; i < canvasPoints.length; i++) {
      const startPoint = canvasPoints[i];
      const endPoint = canvasPoints[(i + 1) % canvasPoints.length];

      const edgeId =
        holeIndex !== null
          ? `edge-${annotationIndex}-hole-${holeIndex}-${i}`
          : `edge-${annotationIndex}-${i}`;

      const edgeLine = new Konva.Line({
        points: [startPoint[0], startPoint[1], endPoint[0], endPoint[1]],
        stroke: color,
        strokeWidth: 16,
        opacity: 0,
        lineCap: "round",
        lineJoin: "round",
        name: "edge-handle",
        id: edgeId,
      });

      // Hover effects
      edgeLine.on("mouseenter", () => {
        const stage = edgeLine.getStage();
        if (stage) {
          stage.container().style.cursor = "copy";
        }
        edgeLine.opacity(0.3);
        edgeLine.strokeWidth(4);
        this.context.annotationLayer?.batchDraw();
      });

      edgeLine.on("mouseleave", () => {
        const stage = edgeLine.getStage();
        if (stage) {
          stage.container().style.cursor = "default";
        }
        edgeLine.opacity(0);
        edgeLine.strokeWidth(16);
        this.context.annotationLayer?.batchDraw();
      });

      // Click to insert point
      edgeLine.on("click", () => {
        const stage = edgeLine.getStage();
        if (!stage) return;

        const pointerPos = stage.getPointerPosition();
        if (!pointerPos) return;

        onInsertPoint(annotationIndex, i, pointerPos, holeIndex);
      });

      // Allow context menu on edge handles
      if (attachContextMenuHandler) {
        attachContextMenuHandler(
          edgeLine,
          annotationIndex,
          holeIndex ?? undefined
        );
      }

      this.context.annotationLayer.add(edgeLine);
    }
  }

  constrainPointToParentShape(
    parentAnnotation: ImageAnnotationAnswer,
    stagePoint: Konva.Vector2d,
    holeIndex: number | null
  ): Konva.Vector2d {
    // Only constrain when moving a hole point
    if (holeIndex === null || !parentAnnotation) {
      return stagePoint;
    }

    if (parentAnnotation.shape_type === "rectangle") {
      const parentBounds = getParentShapeBounds(parentAnnotation.points);
      const clampedImagePoint = clampToParentBounds(
        this.context.getImageCoordinates(
          [[stagePoint.x, stagePoint.y]],
          this.context.imageNode
        )[0],
        parentBounds
      );
      const [canvasX, canvasY] = this.context.getCanvasCoordinates(
        [clampedImagePoint],
        this.context.imageNode
      )[0];
      return { x: canvasX, y: canvasY };
    }

    if (parentAnnotation.shape_type === "polygon") {
      const polygonCanvasPoints = this.context.getCanvasCoordinates(
        parentAnnotation.points,
        this.context.imageNode
      );

      // Check if point is within parent polygon's bounding box
      if (checkPointWithinParent(stagePoint, polygonCanvasPoints)) {
        // Point is inside, allow free movement
        return stagePoint;
      }

      // Point is outside, snap to closest point on polygon boundary
      const polygonPoints = polygonCanvasPoints.map(([x, y]) => ({ x, y }));
      return getClosestPointOnPolygon(stagePoint, polygonPoints);
    }

    return stagePoint;
  }

  insertPointOnEdge(
    annotation: ImageAnnotationAnswer,
    annotationIndex: number,
    edgeIndex: number,
    position: { x: number; y: number },
    holeIndex: number | null
  ): void {
    const constrainedPos = this.constrainPointToParentShape(
      annotation,
      position,
      holeIndex
    );

    // Convert canvas position to image coordinates
    const imageCoords = this.context.getImageCoordinates(
      [[constrainedPos.x, constrainedPos.y]],
      this.context.imageNode
    )[0];

    if (holeIndex !== null) {
      const hole = annotation.holes?.[holeIndex];
      if (hole && hole.shape_type === "polygon") {
        hole.points.splice(edgeIndex + 1, 0, imageCoords);
      }
    } else if (annotation.shape_type === "polygon") {
      annotation.points.splice(edgeIndex + 1, 0, imageCoords);
    }

    // Update the annotation shape visually
    this.updateAnnotationShape(annotation, annotationIndex);
    this.context.updateAnswer();

    // Re-render anchor points to show the new point
    if (this.context.renderAnchorPoints) {
      this.context.renderAnchorPoints(annotationIndex);
    }
  }

  updateAnnotationFromDrag(
    annotation: ImageAnnotationAnswer,
    pointIndex: number,
    newPos: { x: number; y: number },
    holeIndex: number | null
  ): void {
    const imageCoords = this.context.getImageCoordinates(
      [[newPos.x, newPos.y]],
      this.context.imageNode
    )[0];

    const target =
      holeIndex !== null ? annotation.holes?.[holeIndex] : annotation;
    if (!target) return;

    // Update the point - assumes this tool is called for polygon shapes only
    target.points[pointIndex] = imageCoords;
  }
}
