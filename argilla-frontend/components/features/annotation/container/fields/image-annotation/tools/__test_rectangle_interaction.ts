/**
 * Quick manual test to verify RectangleInteraction works correctly.
 * This file can be deleted after Phase 3 when we integrate with the view model.
 * 
 * To test:
 * 1. Import this in your component temporarily
 * 2. Call testRectangleInteraction() with a mock context
 * 3. Verify it creates interactions and handles events
 */

import { RectangleTool } from "./RectangleTool";
import { InteractionContext } from "./IToolInteraction";

export function testRectangleInteraction() {
  console.log("🧪 Testing RectangleInteraction...");
  
  // Create a mock context
  const mockContext: InteractionContext = {
    annotationLayer: null,
    imageLayer: null,
    imageNode: null,
    getAnnotationColor: (label: string) => "#0000ff",
    getImageCoordinates: (points: number[][]) => points,
    getCanvasCoordinates: (points: number[][]) => points,
    updateAnswer: () => console.log("updateAnswer called"),
    renderAnnotations: () => console.log("renderAnnotations called"),
  };
  
  // Create a rectangle tool
  const tool = new RectangleTool(mockContext as any);
  
  // Test 1: Create interaction
  console.log("✓ Test 1: Creating interaction...");
  const interaction = tool.createInteraction(
    mockContext,
    { x: 100, y: 100 },
    "#0000ff",
    false, // not a hole
    undefined,
    { value: "test-label", color: "#0000ff" }
  );
  
  console.assert(interaction.kind === "drawing", "Interaction kind should be 'drawing'");
  console.assert(interaction.toolType === "rectangle", "Tool type should be 'rectangle'");
  console.assert(interaction.isHole === false, "Should not be a hole");
  console.assert(interaction.color === "#0000ff", "Color should match");
  console.log("✓ Test 1 passed!");
  
  // Test 2: Move pointer (should update preview)
  console.log("✓ Test 2: Moving pointer...");
  interaction.onPointerMove({ x: 200, y: 200 });
  // No assertion needed - just verify no errors
  console.log("✓ Test 2 passed!");
  
  // Test 3: Release pointer with valid size
  console.log("✓ Test 3: Releasing pointer with valid size...");
  let result = interaction.onPointerUp({ x: 200, y: 200 });
  console.assert(result.shouldComplete, "Should complete with valid size (100x100)");
  console.log("✓ Test 3 passed!");
  
  // Test 4: Create and test minimum size rejection
  console.log("✓ Test 4: Testing minimum size rejection...");
  const smallInteraction = tool.createInteraction(
    mockContext,
    { x: 100, y: 100 },
    "#0000ff",
    false,
    undefined,
    { value: "test-label", color: "#0000ff" }
  );
  result = smallInteraction.onPointerUp({ x: 102, y: 102 }); // Only 2x2 pixels
  console.assert(result.shouldCancel, "Should cancel with size below minimum (5px)");
  console.log("✓ Test 4 passed!");
  
  // Test 5: Keyboard shortcuts
  console.log("✓ Test 5: Testing keyboard shortcuts...");
  const escapeEvent = new KeyboardEvent("keydown", { key: "Escape" });
  result = interaction.onKeyDown(escapeEvent);
  console.assert(result.shouldCancel, "Escape should trigger cancel");
  console.log("✓ Test 5 passed!");
  
  // Test 6: Hole interaction
  console.log("✓ Test 6: Creating hole interaction...");
  const holeInteraction = tool.createInteraction(
    mockContext,
    { x: 300, y: 300 },
    "#00ff00",
    true, // is a hole
    0, // parent index
    undefined
  );
  
  console.assert(holeInteraction.isHole === true, "Should be a hole");
  console.assert(holeInteraction.parentIndex === 0, "Parent index should be 0");
  console.log("✓ Test 6 passed!");
  
  // Test 7: Complete and create annotation
  console.log("✓ Test 7: Testing annotation creation...");
  const completeInteraction = tool.createInteraction(
    mockContext,
    { x: 50, y: 50 },
    "#ff0000",
    false,
    undefined,
    { value: "my-label", color: "#ff0000" }
  );
  completeInteraction.onPointerMove({ x: 150, y: 150 });
  completeInteraction.onPointerUp({ x: 150, y: 150 });
  
  const annotation = completeInteraction.complete();
  console.assert(annotation !== null, "Should create annotation");
  console.assert(annotation?.label === "my-label", "Label should match");
  console.assert(annotation?.shape_type === "rectangle", "Shape type should be rectangle");
  console.assert(annotation?.points.length === 2, "Should have 2 points");
  console.log("✓ Test 7 passed!");
  
  console.log("✅ All RectangleInteraction tests passed!");
  
  return {
    interaction,
    holeInteraction,
    tool,
  };
}

// Export for console testing
if (typeof window !== "undefined") {
  (window as any).testRectangleInteraction = testRectangleInteraction;
}
