import Konva from "konva";
import { ImageAnnotationAnswer } from "~/v1/domain/entities/IAnswer";

/**
 * Context provided to tool interactions for accessing canvas layers and utilities
 */
export interface InteractionContext {
  annotationLayer: Konva.Layer | null;
  imageLayer: Konva.Layer | null;
  imageNode: Konva.Image | null;
  getAnnotationColor: (labelValue: string) => string;
  getImageCoordinates: (points: number[][], imageNode: Konva.Image | null) => number[][];
  getCanvasCoordinates: (points: number[][], imageNode: Konva.Image | null) => number[][];
  updateAnswer: () => void;
  renderAnnotations: () => void;
}

/**
 * Result returned by interaction event handlers to signal state transitions
 */
export interface InteractionResult {
  /** Signal that the interaction should complete and create the annotation */
  shouldComplete?: boolean;
  /** Signal that the interaction should be cancelled */
  shouldCancel?: boolean;
  /** Signal that the interaction should continue (default) */
  shouldContinue?: boolean;
}

/**
 * Interface for tool interactions that encapsulate drawing state and behavior.
 * Each tool creates an interaction instance when drawing begins, which owns
 * all state and handles all events until the drawing is complete or cancelled.
 */
export interface ToolInteraction {
  // Metadata
  /** The kind of interaction - currently only "drawing" */
  readonly kind: "drawing";
  /** The type of tool creating this interaction (e.g., "rectangle", "polygon") */
  readonly toolType: string;
  /** Whether this is drawing a hole inside a parent shape */
  readonly isHole: boolean;
  /** Index of the parent annotation if drawing a hole */
  readonly parentIndex?: number;
  /** Color for the shape being drawn */
  readonly color: string;
  
  // Event handlers
  /**
   * Handle pointer down event
   * @param pos - Pointer position in stage coordinates
   * @returns Result indicating whether to complete, cancel, or continue
   */
  onPointerDown(pos: { x: number; y: number }): InteractionResult;
  
  /**
   * Handle pointer move event
   * @param pos - Pointer position in stage coordinates
   */
  onPointerMove(pos: { x: number; y: number }): void;
  
  /**
   * Handle pointer up event
   * @param pos - Pointer position in stage coordinates
   * @returns Result indicating whether to complete, cancel, or continue
   */
  onPointerUp(pos: { x: number; y: number }): InteractionResult;
  
  /**
   * Handle keyboard event
   * @param e - Keyboard event
   * @returns Result indicating whether to complete, cancel, or continue
   */
  onKeyDown(e: KeyboardEvent): InteractionResult;
  
  // Lifecycle methods
  /**
   * Complete the interaction and return the created annotation
   * @returns The created annotation or null if creation failed
   */
  complete(): ImageAnnotationAnswer | null;
  
  /**
   * Cancel the interaction without creating an annotation
   */
  cancel(): void;
  
  /**
   * Cleanup any temporary visual elements (shapes, circles, etc.)
   */
  cleanup(): void;
  
  // Optional callbacks for controller to execute
  /**
   * Optional callback to highlight the parent shape when drawing holes
   */
  onParentHighlight?: () => void;
  
  /**
   * Optional callback to remove parent shape highlight
   */
  onParentUnhighlight?: () => void;
}
