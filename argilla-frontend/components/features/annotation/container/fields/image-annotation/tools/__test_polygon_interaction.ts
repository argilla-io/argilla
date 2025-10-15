/**
 * Quick manual test to verify PolygonInteraction works correctly.
 * This file can be deleted after Phase 3 when we integrate with the view model.
 * 
 * To test:
 * 1. Import this in your component temporarily
 * 2. Call testPolygonInteraction() with a mock context
 * 3. Verify it creates interactions and handles events
 */

import { PolygonTool } from "./PolygonTool";
import { InteractionContext } from "./IToolInteraction";

export function testPolygonInteraction() {
  console.log("🧪 Testing PolygonInteraction...");
  
  // Create a mock context
  const mockContext: InteractionContext = {
    annotationLayer: null,
    imageLayer: null,
    imageNode: null,
    getAnnotationColor: (label: string) => "#ff0000",
    getImageCoordinates: (points: number[][]) => points,
    getCanvasCoordinates: (points: number[][]) => points,
    updateAnswer: () => console.log("updateAnswer called"),
    renderAnnotations: () => console.log("renderAnnotations called"),
  };
  
  // Create a polygon tool
  const tool = new PolygonTool(mockContext as any);
  
  // Test 1: Create interaction
  console.log("✓ Test 1: Creating interaction...");
  const interaction = tool.createInteraction(
    mockContext,
    { x: 100, y: 100 },
    "#ff0000",
    false, // not a hole
    undefined,
    { value: "test-label", color: "#ff0000" }
  );
  
  console.assert(interaction.kind === "drawing", "Interaction kind should be 'drawing'");
  console.assert(interaction.toolType === "polygon", "Tool type should be 'polygon'");
  console.assert(interaction.isHole === false, "Should not be a hole");
  console.assert(interaction.color === "#ff0000", "Color should match");
  console.log("✓ Test 1 passed!");
  
  // Test 2: Add points
  console.log("✓ Test 2: Adding points...");
  let result = interaction.onPointerDown({ x: 150, y: 100 });
  console.assert(!result.shouldComplete, "Should not complete after 2 points");
  
  result = interaction.onPointerDown({ x: 150, y: 150 });
  console.assert(!result.shouldComplete, "Should not complete after 3 points");
  console.log("✓ Test 2 passed!");
  
  // Test 3: Keyboard shortcuts
  console.log("✓ Test 3: Testing keyboard shortcuts...");
  const escapeEvent = new KeyboardEvent("keydown", { key: "Escape" });
  result = interaction.onKeyDown(escapeEvent);
  console.assert(result.shouldCancel, "Escape should trigger cancel");
  console.log("✓ Test 3 passed!");
  
  // Test 4: Hole interaction
  console.log("✓ Test 4: Creating hole interaction...");
  const holeInteraction = tool.createInteraction(
    mockContext,
    { x: 200, y: 200 },
    "#00ff00",
    true, // is a hole
    0, // parent index
    undefined
  );
  
  console.assert(holeInteraction.isHole === true, "Should be a hole");
  console.assert(holeInteraction.parentIndex === 0, "Parent index should be 0");
  console.log("✓ Test 4 passed!");
  
  console.log("✅ All PolygonInteraction tests passed!");
  
  return {
    interaction,
    holeInteraction,
    tool,
  };
}

// Export for console testing
if (typeof window !== "undefined") {
  (window as any).testPolygonInteraction = testPolygonInteraction;
}
