import { PolygonTool } from "./PolygonTool";
import { InteractionContext } from "./IToolInteraction";

const createMockContext = (): InteractionContext => ({
  annotationLayer: null,
  imageLayer: null,
  imageNode: null,
  getAnnotationColor: (_label: string) => "#ff0000",
  getImageCoordinates: (points: number[][]) => points,
  getCanvasCoordinates: (points: number[][]) => points,
  updateAnswer: jest.fn(),
  renderAnnotations: jest.fn(),
});

describe("PolygonTool", () => {
  describe("createInteraction", () => {
    test("should create polygon interaction with correct properties", () => {
      const mockContext = createMockContext();
      const tool = new PolygonTool(mockContext as any);

      const interaction = tool.createInteraction(
        mockContext,
        { x: 100, y: 100 },
        "#ff0000",
        false,
        undefined,
        { value: "test-label", color: "#ff0000" }
      );

      expect(interaction.kind).toBe("drawing");
      expect(interaction.toolType).toBe("polygon");
      expect(interaction.isHole).toBe(false);
      expect(interaction.color).toBe("#ff0000");
    });

    test("should create hole interaction with parent index", () => {
      const mockContext = createMockContext();
      const tool = new PolygonTool(mockContext as any);

      const holeInteraction = tool.createInteraction(
        mockContext,
        { x: 200, y: 200 },
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

  describe("polygon drawing", () => {
    test("should not complete polygon with less than 3 points", () => {
      const mockContext = createMockContext();
      const tool = new PolygonTool(mockContext as any);

      const interaction = tool.createInteraction(
        mockContext,
        { x: 100, y: 100 },
        "#ff0000",
        false,
        undefined,
        { value: "test-label", color: "#ff0000" }
      );

      let result = interaction.onPointerDown({ x: 150, y: 100 });
      expect(result.shouldComplete).toBeFalsy();

      result = interaction.onPointerDown({ x: 150, y: 150 });
      expect(result.shouldComplete).toBeFalsy();
    });

    test("should handle pointer move without errors", () => {
      const mockContext = createMockContext();
      const tool = new PolygonTool(mockContext as any);

      const interaction = tool.createInteraction(
        mockContext,
        { x: 100, y: 100 },
        "#ff0000",
        false,
        undefined,
        { value: "test-label", color: "#ff0000" }
      );

      expect(() => {
        interaction.onPointerMove({ x: 150, y: 150 });
      }).not.toThrow();
    });
  });

  describe("keyboard shortcuts", () => {
    test("should cancel on Escape key", () => {
      const mockContext = createMockContext();
      const tool = new PolygonTool(mockContext as any);

      const interaction = tool.createInteraction(
        mockContext,
        { x: 100, y: 100 },
        "#ff0000",
        false,
        undefined,
        { value: "test-label", color: "#ff0000" }
      );

      const escapeEvent = new KeyboardEvent("keydown", { key: "Escape" });
      const result = interaction.onKeyDown(escapeEvent);

      expect(result.shouldCancel).toBe(true);
    });
  });

  describe("complete", () => {
    test("should create annotation with correct properties", () => {
      const mockContext = createMockContext();
      const tool = new PolygonTool(mockContext as any);

      const interaction = tool.createInteraction(
        mockContext,
        { x: 50, y: 50 },
        "#ff0000",
        false,
        undefined,
        { value: "my-label", color: "#ff0000" }
      );

      interaction.onPointerDown({ x: 100, y: 50 });
      interaction.onPointerDown({ x: 100, y: 100 });
      interaction.onPointerDown({ x: 50, y: 100 });

      const annotation = interaction.complete();

      expect(annotation).not.toBeNull();
      expect(annotation?.label).toBe("my-label");
      expect(annotation?.shape_type).toBe("polygon");
      expect(annotation?.points.length).toBeGreaterThanOrEqual(4);
    });
  });
});
