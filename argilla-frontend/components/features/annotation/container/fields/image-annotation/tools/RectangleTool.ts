import Konva from "konva";
import { getParentShapeBounds, clampToParentBounds } from "../utils/geometry";
import { updateRectanglePoint } from "../utils/konvaShapes";
import { ANNOTATION_SHORTCUTS, matchesKey } from "../utils/keyboardShortcuts";
import { BaseAnnotationTool } from "./BaseAnnotationTool";
import { DrawingState, AnchorPointConfig } from "./IAnnotationTool";
import {
  ToolInteraction,
  InteractionContext,
  InteractionResult,
} from "./IToolInteraction";
import { ImageAnnotationAnswer } from "~/v1/domain/entities/IAnswer";

interface RectangleDrawingState extends DrawingState {
  kind: "draw-rect" | "draw-hole-rect";
  start: { x: number; y: number };
  color: string;
  parentIndex?: number;
}

/**
 * Interaction implementation for rectangle drawing.
 * Encapsulates all state and behavior for drawing a rectangle annotation.
 */
class RectangleInteraction implements ToolInteraction {
  readonly kind = "drawing" as const;
  readonly toolType = "rectangle";
  readonly isHole: boolean;
  readonly parentIndex?: number;
  readonly color: string;

  private startPos: { x: number; y: number };
  private currentPos: { x: number; y: number };
  private drawingShape: Konva.Rect | null = null;
  private readonly MIN_SIZE = 5;

  constructor(
    private context: InteractionContext,
    private selectedLabel: { value: string; color: string } | undefined,
    startPos: { x: number; y: number },
    color: string,
    isHole: boolean,
    parentIndex?: number
  ) {
    this.startPos = startPos;
    this.currentPos = startPos;
    this.color = color;
    this.isHole = isHole;
    this.parentIndex = parentIndex;

    // Initialize drawing shape
    this.drawingShape = new Konva.Rect({
      x: startPos.x,
      y: startPos.y,
      width: 0,
      height: 0,
      stroke: color,
      strokeWidth: 2,
      dash: [5, 5],
    });
    context.annotationLayer?.add(this.drawingShape);
    context.annotationLayer?.batchDraw();
  }

  onPointerDown(_pos: { x: number; y: number }): InteractionResult {
    // Rectangle doesn't handle additional pointer downs during drawing
    return { shouldContinue: true };
  }

  onPointerMove(pos: { x: number; y: number }): void {
    this.currentPos = pos;
    if (this.drawingShape) {
      const width = pos.x - this.startPos.x;
      const height = pos.y - this.startPos.y;
      this.drawingShape.width(width);
      this.drawingShape.height(height);
      this.context.annotationLayer?.batchDraw();
    }
  }

  onPointerUp(pos: { x: number; y: number }): InteractionResult {
    this.currentPos = pos;

    const width = Math.abs(pos.x - this.startPos.x);
    const height = Math.abs(pos.y - this.startPos.y);

    // Check minimum size
    if (width < this.MIN_SIZE || height < this.MIN_SIZE) {
      return { shouldCancel: true };
    }

    return { shouldComplete: true };
  }

  onKeyDown(e: KeyboardEvent): InteractionResult {
    if (matchesKey(e, ANNOTATION_SHORTCUTS.CANCEL)) {
      e.preventDefault();
      return { shouldCancel: true };
    }
    return { shouldContinue: true };
  }

  complete(): ImageAnnotationAnswer | null {
    const width = Math.abs(this.currentPos.x - this.startPos.x);
    const height = Math.abs(this.currentPos.y - this.startPos.y);

    // Verify minimum size
    if (width < this.MIN_SIZE || height < this.MIN_SIZE) {
      return null;
    }

    // Convert to image coordinates
    const imageCoords = this.context.getImageCoordinates(
      [
        [this.startPos.x, this.startPos.y],
        [this.currentPos.x, this.currentPos.y],
      ],
      this.context.imageNode
    );

    if (this.isHole) {
      // Hole creation is handled by the controller
      // Return null to signal that the controller should handle it
      return null;
    }

    if (!this.selectedLabel) {
      return null;
    }

    return {
      label: this.selectedLabel.value,
      points: imageCoords,
      shape_type: "rectangle",
      flags: {},
    };
  }

  cancel(): void {
    this.cleanup();
  }

  cleanup(): void {
    if (this.drawingShape) {
      this.drawingShape.destroy();
      this.drawingShape = null;
    }
    this.context.annotationLayer?.batchDraw();
  }

  /**
   * Get the start and current positions for hole creation (used by controller)
   */
  getStartPos(): { x: number; y: number } {
    return this.startPos;
  }

  getCurrentPos(): { x: number; y: number } {
    return this.currentPos;
  }
}

/**
 * Tool for drawing and editing rectangle annotations
 */
export class RectangleTool extends BaseAnnotationTool {
  readonly shapeType = "rectangle";

  createInteraction(
    context: InteractionContext,
    startPos: { x: number; y: number },
    color: string,
    isHole: boolean,
    parentIndex?: number,
    selectedLabel?: { value: string; color: string }
  ): ToolInteraction {
    return new RectangleInteraction(
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
  ): RectangleDrawingState {
    this.drawingShape = new Konva.Rect({
      x: pos.x,
      y: pos.y,
      width: 0,
      height: 0,
      stroke: color,
      strokeWidth: 2,
      dash: [5, 5],
    });
    this.context.annotationLayer?.add(this.drawingShape);
    this.context.annotationLayer?.batchDraw();

    return isHole
      ? {
          kind: "draw-hole-rect",
          start: pos,
          color,
          parentIndex: parentIndex!,
        }
      : {
          kind: "draw-rect",
          start: pos,
          color,
        };
  }

  updateDrawing(state: DrawingState, pos: { x: number; y: number }): void {
    const rectState = state as RectangleDrawingState;
    if (this.drawingShape) {
      const rect = this.drawingShape as Konva.Rect;
      const width = pos.x - rectState.start.x;
      const height = pos.y - rectState.start.y;
      rect.width(width);
      rect.height(height);
      this.context.annotationLayer?.batchDraw();
    }
  }

  completeDrawing(
    state: DrawingState,
    _annotations: ImageAnnotationAnswer[],
    selectedLabel: { value: string; color: string } | undefined
  ): ImageAnnotationAnswer | null {
    const rectState = state as RectangleDrawingState;

    // Convert to image coordinates
    const imageCoords = this.context.getImageCoordinates(
      [
        [rectState.start.x, rectState.start.y],
        [rectState.start.x, rectState.start.y], // Will be updated by caller with actual end position
      ],
      this.context.imageNode
    );

    if (rectState.kind === "draw-hole-rect") {
      // Return null - hole creation is handled by the caller
      return null;
    }

    // Normal annotation creation
    if (!selectedLabel) {
      return null;
    }

    return {
      label: selectedLabel.value,
      points: imageCoords,
      shape_type: "rectangle",
      flags: {},
    };
  }

  cancelDrawing(state: DrawingState): void {
    this.cleanupDrawing(state);
  }

  cleanupDrawing(_state: DrawingState): void {
    if (this.drawingShape) {
      this.drawingShape.destroy();
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

    if (canvasPoints.length !== 2) return;

    const [p1, p2] = canvasPoints;
    const corners = [
      { x: p1[0], y: p1[1] }, // top-left
      { x: p2[0], y: p1[1] }, // top-right
      { x: p2[0], y: p2[1] }, // bottom-right
      { x: p1[0], y: p2[1] }, // bottom-left
    ];

    corners.forEach((corner, pointIndex) => {
      this.createAnchorPoint(corner.x, corner.y, color, {
        ...config,
        pointIndex,
      });
    });

    // Render hole anchors - delegate to appropriate tool based on hole shape type
    annotation.holes?.forEach((hole, holeIndex) => {
      if (hole.shape_type === "rectangle") {
        // Render rectangle holes directly
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
      } else if (
        hole.shape_type === "polygon" &&
        this.context.getToolForShape
      ) {
        // Delegate polygon holes to PolygonTool
        const polyTool = this.context.getToolForShape("polygon");
        if (polyTool) {
          const holeCanvasPoints = this.context.getCanvasCoordinates(
            hole.points,
            this.context.imageNode
          );

          // Render edge handles FIRST (so they're behind anchor points)
          if (polyTool.renderEdgeHandles) {
            polyTool.renderEdgeHandles(
              annotation,
              annotationIndex,
              holeCanvasPoints,
              color,
              holeIndex,
              (annIdx, edgeIdx, pos, holeIdx) => {
                if (polyTool.insertPointOnEdge) {
                  polyTool.insertPointOnEdge(
                    annotation,
                    annIdx,
                    edgeIdx,
                    pos,
                    holeIdx
                  );
                }
              },
              config.attachContextMenuHandler
            );
          }

          // Render vertex anchor points LAST (so they're on top and clickable)
          holeCanvasPoints.forEach((point, pointIndex) => {
            this.createAnchorPoint(point[0], point[1], color, {
              ...config,
              pointIndex,
              holeIndex,
            });
          });
        }
      }
    });

    this.context.annotationLayer?.batchDraw();
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

    return stagePoint;
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

    // Update the rectangle point - assumes this tool is called for rectangle shapes only
    target.points = updateRectanglePoint(
      target.points,
      pointIndex,
      imageCoords
    );
  }
}
