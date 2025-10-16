import { RectangleTool } from "./RectangleTool";
import { InteractionContext } from "./IToolInteraction";

const createMockContext = (): InteractionContext => ({
  annotationLayer: null,
  imageLayer: null,
  imageNode: null,
  getAnnotationColor: (_label: string) => "#0000ff",
  getImageCoordinates: (points: number[][]) => points,
  getCanvasCoordinates: (points: number[][]) => points,
  updateAnswer: jest.fn(),
  renderAnnotations: jest.fn(),
});

describe("RectangleTool", () => {
  describe("createInteraction", () => {
    test("should create rectangle interaction with correct properties", () => {
      const mockContext = createMockContext();
      const tool = new RectangleTool(mockContext as any);

      const interaction = tool.createInteraction(
        mockContext,
        { x: 100, y: 100 },
        "#0000ff",
        false,
        undefined,
        { value: "test-label", color: "#0000ff" }
      );

      expect(interaction.kind).toBe("drawing");
      expect(interaction.toolType).toBe("rectangle");
      expect(interaction.isHole).toBe(false);
      expect(interaction.color).toBe("#0000ff");
    });

    test("should create hole interaction with parent index", () => {
      const mockContext = createMockContext();
      const tool = new RectangleTool(mockContext as any);

      const holeInteraction = tool.createInteraction(
        mockContext,
        { x: 300, y: 300 },
        "#00ff00",
        true,
        0,
        undefined
      );

      expect(holeInteraction.isHole).toBe(true);
      expect(holeInteraction.parentIndex).toBe(0);
      expect(holeInteraction.color).toBe("#00ff00");
    });
  });

  describe("rectangle drawing", () => {
    test("should handle pointer move without errors", () => {
      const mockContext = createMockContext();
      const tool = new RectangleTool(mockContext as any);

      const interaction = tool.createInteraction(
        mockContext,
        { x: 100, y: 100 },
        "#0000ff",
        false,
        undefined,
        { value: "test-label", color: "#0000ff" }
      );

      expect(() => {
        interaction.onPointerMove({ x: 200, y: 200 });
      }).not.toThrow();
    });

    test("should complete with valid size", () => {
      const mockContext = createMockContext();
      const tool = new RectangleTool(mockContext as any);

      const interaction = tool.createInteraction(
        mockContext,
        { x: 100, y: 100 },
        "#0000ff",
        false,
        undefined,
        { value: "test-label", color: "#0000ff" }
      );

      const result = interaction.onPointerUp({ x: 200, y: 200 });
      expect(result.shouldComplete).toBe(true);
    });

    test("should cancel with size below minimum", () => {
      const mockContext = createMockContext();
      const tool = new RectangleTool(mockContext as any);

      const smallInteraction = tool.createInteraction(
        mockContext,
        { x: 100, y: 100 },
        "#0000ff",
        false,
        undefined,
        { value: "test-label", color: "#0000ff" }
      );

      const result = smallInteraction.onPointerUp({ x: 102, y: 102 });
      expect(result.shouldCancel).toBe(true);
    });
  });

  describe("keyboard shortcuts", () => {
    test("should cancel on Escape key", () => {
      const mockContext = createMockContext();
      const tool = new RectangleTool(mockContext as any);

      const interaction = tool.createInteraction(
        mockContext,
        { x: 100, y: 100 },
        "#0000ff",
        false,
        undefined,
        { value: "test-label", color: "#0000ff" }
      );

      const escapeEvent = new KeyboardEvent("keydown", { key: "Escape" });
      const result = interaction.onKeyDown(escapeEvent);

      expect(result.shouldCancel).toBe(true);
    });
  });

  describe("complete", () => {
    test("should create annotation with correct properties", () => {
      const mockContext = createMockContext();
      const tool = new RectangleTool(mockContext as any);

      const interaction = tool.createInteraction(
        mockContext,
        { x: 50, y: 50 },
        "#ff0000",
        false,
        undefined,
        { value: "my-label", color: "#ff0000" }
      );

      interaction.onPointerMove({ x: 150, y: 150 });
      interaction.onPointerUp({ x: 150, y: 150 });

      const annotation = interaction.complete();

      expect(annotation).not.toBeNull();
      expect(annotation?.label).toBe("my-label");
      expect(annotation?.shape_type).toBe("rectangle");
      expect(annotation?.points.length).toBe(2);
    });
  });
});
