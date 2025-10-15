import Konva from "konva";
import { IAnnotationTool, ToolContext, AnchorPointConfig, DrawingState } from "./IAnnotationTool";
import { ToolInteraction, InteractionContext } from "./IToolInteraction";
import { ImageAnnotationAnswer } from "~/v1/domain/entities/IAnswer";
import { getAnnotationNodes, updateKonvaShape } from "../utils/konvaShapeUtils";

/**
 * Base class for annotation tools providing common functionality
 */
export abstract class BaseAnnotationTool implements IAnnotationTool {
  protected context: ToolContext;
  protected drawingShape: Konva.Shape | null = null;

  constructor(context: ToolContext) {
    this.context = context;
  }

  abstract readonly shapeType: string;

  abstract createInteraction(
    context: InteractionContext,
    startPos: { x: number; y: number },
    color: string,
    isHole: boolean,
    parentIndex?: number,
    selectedLabel?: { value: string; color: string }
  ): ToolInteraction;

  abstract startDrawing(
    pos: { x: number; y: number },
    color: string,
    isHole: boolean,
    parentIndex?: number
  ): DrawingState;

  abstract updateDrawing(state: DrawingState, pos: { x: number; y: number }): void;

  abstract completeDrawing(
    state: DrawingState,
    annotations: ImageAnnotationAnswer[],
    selectedLabel: { value: string; color: string } | undefined
  ): ImageAnnotationAnswer | null;

  abstract cancelDrawing(state: DrawingState): void;

  abstract cleanupDrawing(state: DrawingState): void;

  abstract renderAnchorPoints(
    annotation: ImageAnnotationAnswer,
    annotationIndex: number,
    color: string,
    config: AnchorPointConfig
  ): void;

  abstract updateAnnotationFromDrag(
    annotation: ImageAnnotationAnswer,
    pointIndex: number,
    newPos: { x: number; y: number },
    holeIndex: number | null
  ): void;

  /**
   * Common implementation for creating anchor points
   */
  createAnchorPoint(
    x: number,
    y: number,
    color: string,
    config: AnchorPointConfig
  ): Konva.Circle {
    const { annotationIndex, pointIndex, holeIndex } = config;
    const anchorId =
      holeIndex !== null
        ? `anchor-${annotationIndex}-hole-${holeIndex}-${pointIndex}`
        : `anchor-${annotationIndex}-${pointIndex}`;

    const anchor = new Konva.Circle({
      x,
      y,
      radius: 6,
      fill: "white",
      stroke: color,
      strokeWidth: 2,
      draggable: true,
      name: "anchor-point",
      id: anchorId,
    });

    // Change cursor on hover
    anchor.on("mouseenter", () => {
      const stage = anchor.getStage();
      if (stage) {
        stage.container().style.cursor = "move";
      }
      anchor.radius(8);
      this.context.annotationLayer?.batchDraw();
    });

    anchor.on("mouseleave", () => {
      const stage = anchor.getStage();
      if (stage) {
        stage.container().style.cursor = "default";
      }
      anchor.radius(6);
      this.context.annotationLayer?.batchDraw();
    });

    // Handle dragging
    if (config.onDragStart) {
      anchor.on("dragstart", () => {
        config.onDragStart!(annotationIndex, pointIndex, holeIndex);
      });
    }

    if (config.onDragMove) {
      anchor.on("dragmove", () => {
        config.onDragMove!(annotationIndex, pointIndex, anchor.position(), holeIndex);
        this.context.annotationLayer?.batchDraw();
      });
    }

    if (config.onDragEnd) {
      anchor.on("dragend", () => {
        config.onDragEnd!(annotationIndex);
        const stage = anchor.getStage();
        if (stage) {
          stage.container().style.cursor = "default";
        }
      });
    }

    // Allow context menu on anchor points
    if (config.attachContextMenuHandler) {
      config.attachContextMenuHandler(anchor, annotationIndex, holeIndex ?? undefined);
    }

    this.context.annotationLayer?.add(anchor);
    return anchor;
  }

  /**
   * Common implementation for removing anchor points
   */
  removeAnchorPoints(): void {
    if (!this.context.annotationLayer) return;
    this.context.annotationLayer.find(".anchor-point").forEach((anchor) => anchor.destroy());
    this.context.annotationLayer.find(".edge-handle").forEach((edge) => edge.destroy());
    this.context.annotationLayer.find(".parent-boundary-guide").forEach((guide) => guide.destroy());
    this.context.annotationLayer.batchDraw();
  }

  /**
   * Common implementation for updating annotation shape
   */
  updateAnnotationShape(
    annotation: ImageAnnotationAnswer,
    annotationIndex: number
  ): void {
    if (!this.context.annotationLayer) return;

    const { element, parentShape } = getAnnotationNodes(
      this.context.annotationLayer,
      annotationIndex
    );
    if (!element || !parentShape) return;

    // Update parent shape
    updateKonvaShape(
      parentShape,
      annotation.shape_type,
      this.context.getCanvasCoordinates(annotation.points, this.context.imageNode)
    );

    // Update hole shapes if they exist
    if (element instanceof Konva.Group && annotation.holes) {
      annotation.holes.forEach((hole, holeIndex) => {
        const holeShape = element.findOne(
          `#annotation-${annotationIndex}-hole-${holeIndex}`
        );
        if (holeShape) {
          updateKonvaShape(
            holeShape as Konva.Shape,
            hole.shape_type,
            this.context.getCanvasCoordinates(hole.points, this.context.imageNode)
          );
        }
      });
    }

    this.context.annotationLayer.batchDraw();
  }

  /**
   * Default implementation - no constraint
   */
  constrainPointToParentShape(
    parentAnnotation: ImageAnnotationAnswer,
    stagePoint: Konva.Vector2d,
    holeIndex: number | null
  ): Konva.Vector2d {
    return stagePoint;
  }

  /**
   * Render parent boundary guide when editing holes
   */
  protected renderParentBoundaryGuide(
    annotation: ImageAnnotationAnswer,
    annotationIndex: number,
    color: string
  ): void {
    if (!this.context.annotationLayer) return;

    const canvasPoints = this.context.getCanvasCoordinates(
      annotation.points,
      this.context.imageNode
    );

    let boundaryShape: Konva.Shape | null = null;

    if (annotation.shape_type === "rectangle" && canvasPoints.length === 2) {
      const [p1, p2] = canvasPoints;
      boundaryShape = new Konva.Rect({
        x: Math.min(p1[0], p2[0]),
        y: Math.min(p1[1], p2[1]),
        width: Math.abs(p2[0] - p1[0]),
        height: Math.abs(p2[1] - p1[1]),
        stroke: color,
        strokeWidth: 2,
        dash: [8, 4],
        opacity: 0.5,
        name: "parent-boundary-guide",
        listening: false,
      });
    } else if (annotation.shape_type === "polygon") {
      const points = canvasPoints.flat();
      boundaryShape = new Konva.Line({
        points,
        stroke: color,
        strokeWidth: 2,
        dash: [8, 4],
        opacity: 0.5,
        closed: true,
        name: "parent-boundary-guide",
        listening: false,
      });
    }

    if (boundaryShape) {
      this.context.annotationLayer.add(boundaryShape);
      boundaryShape.moveToBottom();
    }
  }
}
