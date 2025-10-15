import Konva from "konva";
import {
  initPolyDrawing,
  updatePolygonPreview,
  addPolygonPoint as addPolyPoint,
  flatPointsToCoordinatePairs,
  cleanupPolygonDrawing as cleanupPolyDrawing,
} from "../utils/drawingModeHelpers";
import {
  getParentShapeBounds,
  clampToParentBounds,
  getClosestPointOnPolygon,
  isPointWithinParent as checkPointWithinParent,
} from "../utils/geometryUtils";
import {
  createPointCircle,
} from "../utils/konvaShapeUtils";
import { BaseAnnotationTool } from "./BaseAnnotationTool";
import { DrawingState, AnchorPointConfig } from "./IAnnotationTool";
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
 * Tool for drawing and editing polygon annotations
 */
export class PolygonTool extends BaseAnnotationTool {
  readonly shapeType = "polygon";
  private readonly CLOSE_THRESHOLD = 10;

  startDrawing(
    pos: { x: number; y: number },
    color: string,
    isHole: boolean,
    parentIndex?: number
  ): PolygonDrawingState {
    const drawColor = color || "#cccccc";
    const result = initPolyDrawing(
      pos,
      drawColor,
      this.context.annotationLayer,
      createPointCircle
    );

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
    updatePolygonPreview(
      polyState.previewLine,
      polyState.points,
      pos,
      polyState.circles,
      polyState.color,
      this.CLOSE_THRESHOLD,
      this.context.annotationLayer
    );
  }

  addPoint(
    state: DrawingState,
    pos: { x: number; y: number }
  ): { state: DrawingState; shouldComplete: boolean } {
    const polyState = state as PolygonDrawingState;
    const drawColor = polyState.color || "#cccccc";

    const result = addPolyPoint(
      pos,
      drawColor,
      polyState.points,
      this.drawingShape as Konva.Line,
      polyState.circles,
      this.context.annotationLayer,
      this.CLOSE_THRESHOLD,
      createPointCircle
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
    annotations: ImageAnnotationAnswer[],
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
    cleanupPolyDrawing(
      this.drawingShape,
      polyState.circles,
      polyState.previewLine
    );

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
      } else if (hole.shape_type === "rectangle" && this.context.getToolForShape) {
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
    annotation: ImageAnnotationAnswer,
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
        attachContextMenuHandler(edgeLine, annotationIndex, holeIndex ?? undefined);
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
