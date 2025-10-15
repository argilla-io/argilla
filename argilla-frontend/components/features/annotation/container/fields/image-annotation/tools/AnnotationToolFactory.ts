import { IAnnotationTool, ToolContext } from "./IAnnotationTool";
import { RectangleTool } from "./RectangleTool";
import { PolygonTool } from "./PolygonTool";

/**
 * Factory for creating annotation tools
 */
export class AnnotationToolFactory {
  private tools: Map<string, IAnnotationTool> = new Map();
  private context: ToolContext;

  constructor(context: ToolContext) {
    this.context = context;
    this.initializeTools();
  }

  private initializeTools(): void {
    this.tools.set("rectangle", new RectangleTool(this.context));
    this.tools.set("polygon", new PolygonTool(this.context));
  }

  /**
   * Get a tool by its type
   */
  getTool(toolType: string): IAnnotationTool | undefined {
    return this.tools.get(toolType);
  }

  /**
   * Get a tool for a specific shape type
   */
  getToolForShape(shapeType: string): IAnnotationTool | undefined {
    return this.tools.get(shapeType);
  }

  /**
   * Update the context for all tools (e.g., when layers change)
   */
  updateContext(context: ToolContext): void {
    this.context = context;
    this.tools.clear();
    this.initializeTools();
  }
}
