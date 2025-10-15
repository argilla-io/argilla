import Konva from "konva";
import { ImageAnnotationAnswer } from "~/v1/domain/entities/IAnswer";
import { getAnnotationNodes } from "../utils/konvaShapes";
import { getCanvasCoordinates } from "../utils/coordinates";
import { AnnotationToolFactory } from "../tools/AnnotationToolFactory";

export interface AnchorConfig {
  annotationIndex: number;
  pointIndex: number;
  holeIndex: number | null;
  onDragStart: (annIdx: number, ptIdx: number, holeIdx: number | null) => void;
  onDragMove: (annIdx: number, ptIdx: number, pos: { x: number; y: number }, holeIdx: number | null) => void;
  onDragEnd: (annIdx: number) => void;
  attachContextMenuHandler: (element: Konva.Node, annotationIndex: number, holeIndex?: number) => void;
}

export interface RendererDependencies {
  annotationLayer: Konva.Layer | null;
  imageLayer: Konva.Layer | null;
  imageNode: Konva.Image | null;
  toolFactory: AnnotationToolFactory | null;
  getAnnotationColor: (labelValue: string) => string;
  onHoverAnnotation: (index: number) => void;
  onUnhoverAnnotation: () => void;
}

/**
 * AnnotationRenderer - Handles all rendering logic for annotations
 * Separates visualization from business logic, making it easier to add new tools
 */
export class AnnotationRenderer {
  constructor(private deps: RendererDependencies) {}

  /**
   * Create a Konva shape (rectangle or polygon) for an annotation
   */
  private createShape(
    shapeType: string,
    canvasPoints: number[][],
    color: string,
    annotationIndex: number,
    isParent: boolean,
    holeIndex?: number
  ): Konva.Rect | Konva.Line | null {
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
        opacity: isParent ? 0.3 : 1,
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
        opacity: isParent ? 0.3 : 1,
        closed: true,
        listening: true,
      });
    }
    return null;
  }

  /**
   * Attach hover handlers to a Konva element
   */
  private attachHoverHandlers(element: Konva.Node, annotationIndex: number) {
    element.on("mouseenter", () => this.deps.onHoverAnnotation(annotationIndex));
    element.on("mouseleave", () => this.deps.onUnhoverAnnotation());
  }

  /**
   * Render annotation with holes (uses Konva group with composite operation)
   */
  private renderAnnotationWithHoles(
    annotation: ImageAnnotationAnswer,
    index: number,
    color: string,
    canvasPoints: number[][],
    attachContextMenuHandler: (element: Konva.Node, annotationIndex: number, holeIndex?: number) => void
  ) {
    if (!this.deps.annotationLayer) return;

    const group = new Konva.Group({
      id: `annotation-${index}`,
      name: "annotation-group",
    });

    // Create parent shape
    const parentShape = this.createShape(
      annotation.shape_type,
      canvasPoints,
      color,
      index,
      true
    );
    if (parentShape) {
      group.add(parentShape);
    }

    // Render holes as cutouts
    annotation.holes!.forEach((hole, holeIndex) => {
      const holeCanvasPoints = getCanvasCoordinates(hole.points, this.deps.imageNode);
      const holeShape = this.createShape(
        hole.shape_type,
        holeCanvasPoints,
        color,
        index,
        false,
        holeIndex
      );

      if (holeShape) {
        attachContextMenuHandler(holeShape, index, holeIndex);
        holeShape.globalCompositeOperation("destination-out");
        group.add(holeShape);
      }
    });

    // Attach event handlers to group
    this.attachHoverHandlers(group, index);
    attachContextMenuHandler(group, index);

    this.deps.annotationLayer.add(group);
  }

  /**
   * Render simple annotation (no holes)
   */
  private renderSimpleAnnotation(
    annotation: ImageAnnotationAnswer,
    index: number,
    color: string,
    canvasPoints: number[][],
    attachContextMenuHandler: (element: Konva.Node, annotationIndex: number, holeIndex?: number) => void
  ) {
    if (!this.deps.annotationLayer) return;

    const shape = this.createShape(
      annotation.shape_type,
      canvasPoints,
      color,
      index,
      true
    );

    if (shape) {
      this.attachHoverHandlers(shape, index);
      attachContextMenuHandler(shape, index);
      this.deps.annotationLayer.add(shape);
    }
  }

  /**
   * Render all annotations on the canvas
   */
  renderAnnotations(
    annotations: ImageAnnotationAnswer[],
    attachContextMenuHandler: (element: Konva.Node, annotationIndex: number, holeIndex?: number) => void
  ) {
    if (!this.deps.annotationLayer) return;

    // Remove existing annotation shapes and groups
    this.deps.annotationLayer
      .find(".annotation-shape")
      .forEach((shape) => shape.destroy());
    this.deps.annotationLayer
      .find(".annotation-group")
      .forEach((group) => group.destroy());

    // Render each annotation
    annotations.forEach((annotation, index) => {
      const color = this.deps.getAnnotationColor(annotation.label);
      const canvasPoints = getCanvasCoordinates(annotation.points, this.deps.imageNode);
      const hasHoles = annotation.holes && annotation.holes.length > 0;

      if (hasHoles) {
        this.renderAnnotationWithHoles(annotation, index, color, canvasPoints, attachContextMenuHandler);
      } else {
        this.renderSimpleAnnotation(annotation, index, color, canvasPoints, attachContextMenuHandler);
      }
    });

    this.deps.annotationLayer.batchDraw();
  }

  /**
   * Apply highlight styling to an annotation shape
   */
  highlightAnnotation(
    index: number,
    highlight: boolean,
    isEditing: boolean,
    color: string
  ) {
    const { element, parentShape, holeShapes } = getAnnotationNodes(
      this.deps.annotationLayer,
      index
    );
    if (!element || !parentShape) return;

    if (isEditing) {
      (parentShape as any).strokeWidth(4);
      (parentShape as any).shadowColor(color);
      (parentShape as any).shadowBlur(8);
      (parentShape as any).shadowOpacity(0.8);
      (parentShape as any).opacity(0.5);
    } else {
      (parentShape as any).strokeWidth(highlight ? 4 : 2);
      (parentShape as any).shadowBlur(0);
      (parentShape as any).opacity(0.3);
    }

    holeShapes.forEach((holeShape) => {
      (holeShape as any).strokeWidth(isEditing ? 4 : highlight ? 4 : 2);
    });

    const stage = element.getStage();
    if (stage && !isEditing) {
      stage.container().style.cursor = highlight ? "pointer" : "default";
    }

    this.deps.annotationLayer?.batchDraw();
    this.deps.imageLayer?.batchDraw();
  }

  /**
   * Fade all annotations except the one being edited
   */
  fadeNonEditedAnnotations(editingIndex: number, annotations: ImageAnnotationAnswer[]) {
    if (!this.deps.annotationLayer) return;

    annotations.forEach((_, index) => {
      if (index !== editingIndex) {
        const { parentShape } = getAnnotationNodes(this.deps.annotationLayer, index);
        if (parentShape) {
          (parentShape as any).opacity(0.2);
        }
      }
    });

    this.deps.annotationLayer.batchDraw();
  }

  /**
   * Restore opacity for all annotations
   */
  restoreAllAnnotations(annotations: ImageAnnotationAnswer[]) {
    if (!this.deps.annotationLayer) return;

    annotations.forEach((_, index) => {
      const { parentShape } = getAnnotationNodes(this.deps.annotationLayer, index);
      if (parentShape) {
        (parentShape as any).opacity(0.3);
      }
    });

    this.deps.annotationLayer.batchDraw();
  }

  /**
   * Render a visual guide showing the parent shape boundary when editing holes
   */
  renderParentBoundaryGuide(
    annotationIndex: number,
    annotation: ImageAnnotationAnswer,
    color: string
  ) {
    if (!this.deps.annotationLayer) return;

    const canvasPoints = getCanvasCoordinates(annotation.points, this.deps.imageNode);

    // Create a dashed boundary line to show the constraint
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
        listening: false, // Don't interfere with interactions
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
      this.deps.annotationLayer.add(boundaryShape);
      boundaryShape.moveToBottom(); // Keep it behind anchor points
    }
  }

  /**
   * Render anchor points for editing an annotation
   */
  renderAnchorPoints(
    annotation: ImageAnnotationAnswer,
    annotationIndex: number,
    color: string,
    anchorConfig: AnchorConfig
  ) {
    if (!this.deps.annotationLayer || !this.deps.toolFactory) return;

    this.removeAnchorPoints();

    const tool = this.deps.toolFactory.getToolForShape(annotation.shape_type);
    if (!tool) return;

    // Show parent boundary guide if editing a hole
    if (anchorConfig.holeIndex !== null) {
      this.renderParentBoundaryGuide(annotationIndex, annotation, color);
    }

    // Render parent shape anchors
    tool.renderAnchorPoints(annotation, annotationIndex, color, anchorConfig);

    this.deps.annotationLayer.batchDraw();
  }

  /**
   * Remove all anchor points from the canvas
   */
  removeAnchorPoints() {
    if (!this.deps.annotationLayer || !this.deps.toolFactory) return;
    const tool = this.deps.toolFactory.getTool("rectangle"); // Any tool will do for this common operation
    if (tool) {
      tool.removeAnchorPoints();
    }
  }

  /**
   * Highlight parent shape for hole drawing mode
   */
  highlightParentForHoleDrawing(parentIndex: number, annotation: ImageAnnotationAnswer) {
    const { parentShape } = getAnnotationNodes(this.deps.annotationLayer, parentIndex);
    if (!parentShape) return;

    const color = this.deps.getAnnotationColor(annotation.label);

    (parentShape as any).strokeWidth(3);
    (parentShape as any).stroke(color);
    (parentShape as any).dash([10, 5]); // Dashed stroke to indicate hole drawing mode
    (parentShape as any).opacity(0.4);

    this.deps.annotationLayer?.batchDraw();
    this.deps.imageLayer?.batchDraw();
  }
}
