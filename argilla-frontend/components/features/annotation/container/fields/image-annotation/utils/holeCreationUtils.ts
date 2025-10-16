import Konva from "konva";
import { ToolInteraction } from "../tools/IToolInteraction";
import { flatPointsToCoordinatePairs } from "./coordinates";
import { getParentShapeBounds, clampToParentBounds } from "./geometry";
import { ImageAnnotationAnswer } from "~/v1/domain/entities/IAnswer";

/**
 * Extract points from a tool interaction for hole creation
 * Handles both polygon and rectangle tool types
 *
 * @param interaction - The active tool interaction
 * @param getImageCoordinates - Function to convert canvas to image coordinates
 * @param imageNode - The Konva image node
 * @returns Image coordinates or null if extraction fails
 */
export const extractHolePointsFromInteraction = (
  interaction: ToolInteraction,
  getImageCoordinates: (
    points: number[][],
    imageNode: Konva.Image | null
  ) => number[][],
  imageNode: Konva.Image | null
): number[][] | null => {
  if (interaction.toolType === "polygon") {
    const polyInteraction = interaction as any;
    if (polyInteraction.getPoints) {
      const points = flatPointsToCoordinatePairs(polyInteraction.getPoints());
      return getImageCoordinates(points, imageNode);
    }
  } else if (interaction.toolType === "rectangle") {
    const rectInteraction = interaction as any;
    if (rectInteraction.getStartPos && rectInteraction.getCurrentPos) {
      const startPos = rectInteraction.getStartPos();
      const currentPos = rectInteraction.getCurrentPos();
      return getImageCoordinates(
        [
          [startPos.x, startPos.y],
          [currentPos.x, currentPos.y],
        ],
        imageNode
      );
    }
  }
  return null;
};

/**
 * Create and add a hole to a parent annotation
 * Clamps hole coordinates to parent bounds and updates the parent
 *
 * @param parent - The parent annotation to add the hole to
 * @param imageCoords - The hole coordinates in image space
 * @param shapeType - The shape type of the hole ("rectangle" | "polygon")
 * @returns true if hole was added successfully
 */
export const addHoleToParent = (
  parent: ImageAnnotationAnswer,
  imageCoords: number[][],
  shapeType: "rectangle" | "polygon"
): boolean => {
  try {
    // Clamp hole coordinates to parent bounds
    const parentBounds = getParentShapeBounds(parent.points);
    const clampedCoords = imageCoords.map((point) =>
      clampToParentBounds(point, parentBounds)
    );

    // Initialize holes array if needed
    if (!parent.holes) {
      parent.holes = [];
    }

    // Add hole to parent
    parent.holes.push({
      points: clampedCoords,
      shape_type: shapeType,
      flags: {},
    });

    return true;
  } catch (error) {
    console.error("Failed to add hole to parent:", error);
    return false;
  }
};

/**
 * Complete hole creation workflow
 * Extracts points, validates, and adds hole to parent annotation
 *
 * @param interaction - The active tool interaction
 * @param parent - The parent annotation
 * @param getImageCoordinates - Function to convert canvas to image coordinates
 * @param imageNode - The Konva image node
 * @returns true if hole was created successfully
 */
export const completeHoleCreation = (
  interaction: ToolInteraction,
  parent: ImageAnnotationAnswer,
  getImageCoordinates: (
    points: number[][],
    imageNode: Konva.Image | null
  ) => number[][],
  imageNode: Konva.Image | null
): boolean => {
  // Extract points from interaction
  const imageCoords = extractHolePointsFromInteraction(
    interaction,
    getImageCoordinates,
    imageNode
  );

  if (!imageCoords) {
    return false;
  }

  // Add hole to parent
  return addHoleToParent(
    parent,
    imageCoords,
    interaction.toolType as "rectangle" | "polygon"
  );
};
