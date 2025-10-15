/**
 * Mock implementation of Konva for Jest tests
 * This avoids the need for the 'canvas' package in Node.js environment
 */

class MockNode {
  attrs: any = {};
  children: MockNode[] = [];
  parent: MockNode | null = null;

  constructor(config: any = {}) {
    this.attrs = { ...config };
  }

  x(val?: number) {
    if (val !== undefined) this.attrs.x = val;
    return this.attrs.x ?? 0;
  }

  y(val?: number) {
    if (val !== undefined) this.attrs.y = val;
    return this.attrs.y ?? 0;
  }

  width(val?: number) {
    if (val !== undefined) this.attrs.width = val;
    return this.attrs.width ?? 0;
  }

  height(val?: number) {
    if (val !== undefined) this.attrs.height = val;
    return this.attrs.height ?? 0;
  }

  radius(val?: number) {
    if (val !== undefined) this.attrs.radius = val;
    return this.attrs.radius ?? 0;
  }

  fill(val?: string) {
    if (val !== undefined) this.attrs.fill = val;
    return this.attrs.fill;
  }

  stroke(val?: string) {
    if (val !== undefined) this.attrs.stroke = val;
    return this.attrs.stroke;
  }

  strokeWidth(val?: number) {
    if (val !== undefined) this.attrs.strokeWidth = val;
    return this.attrs.strokeWidth ?? 0;
  }

  points(val?: number[]) {
    if (val !== undefined) this.attrs.points = val;
    return this.attrs.points ?? [];
  }

  opacity(val?: number) {
    if (val !== undefined) this.attrs.opacity = val;
    return this.attrs.opacity ?? 1;
  }

  id(val?: string) {
    if (val !== undefined) this.attrs.id = val;
    return this.attrs.id;
  }

  name(val?: string) {
    if (val !== undefined) this.attrs.name = val;
    return this.attrs.name;
  }

  listening(val?: boolean) {
    if (val !== undefined) this.attrs.listening = val;
    return this.attrs.listening ?? true;
  }

  draggable(val?: boolean) {
    if (val !== undefined) this.attrs.draggable = val;
    return this.attrs.draggable ?? false;
  }

  visible(val?: boolean) {
    if (val !== undefined) this.attrs.visible = val;
    return this.attrs.visible ?? true;
  }

  zIndex(val?: number) {
    if (val !== undefined) this.attrs.zIndex = val;
    return this.attrs.zIndex ?? 0;
  }

  add(child: MockNode) {
    this.children.push(child);
    child.parent = this;
    return this;
  }

  destroy() {
    if (this.parent) {
      const index = this.parent.children.indexOf(this);
      if (index > -1) this.parent.children.splice(index, 1);
    }
    this.children = [];
  }

  remove() {
    this.destroy();
  }

  moveToTop() {
    return this;
  }

  moveToBottom() {
    return this;
  }

  getLayer() {
    let node: MockNode | null = this;
    while (node && !(node instanceof MockLayer)) {
      node = node.parent;
    }
    return node;
  }

  find(selector: string) {
    const results: MockNode[] = [];
    const search = (node: MockNode) => {
      if (selector.startsWith("#") && node.attrs.id === selector.slice(1)) {
        results.push(node);
      } else if (selector.startsWith(".") && node.attrs.name === selector.slice(1)) {
        results.push(node);
      }
      node.children.forEach(search);
    };
    search(this);
    return results;
  }

  findOne(selector: string) {
    return this.find(selector)[0] || null;
  }

  on() {
    return this;
  }

  off() {
    return this;
  }

  fire() {
    return this;
  }
}

class MockLayer extends MockNode {
  batchDraw() {
    return this;
  }

  draw() {
    return this;
  }

  clear() {
    return this;
  }
}

class MockStage extends MockNode {
  container() {
    return document.createElement("div");
  }

  batchDraw() {
    return this;
  }

  draw() {
    return this;
  }

  getLayers() {
    return this.children.filter((c) => c instanceof MockLayer);
  }
}

class MockRect extends MockNode {}
class MockCircle extends MockNode {}
class MockLine extends MockNode {
  closed(val?: boolean) {
    if (val !== undefined) this.attrs.closed = val;
    return this.attrs.closed ?? false;
  }

  dash(val?: number[]) {
    if (val !== undefined) this.attrs.dash = val;
    return this.attrs.dash;
  }
}
class MockGroup extends MockNode {}
class MockImage extends MockNode {
  image(val?: any) {
    if (val !== undefined) this.attrs.image = val;
    return this.attrs.image;
  }
}
class MockTransformer extends MockNode {
  nodes(val?: MockNode[]) {
    if (val !== undefined) this.attrs.nodes = val;
    return this.attrs.nodes ?? [];
  }
}

const Konva = {
  Stage: MockStage,
  Layer: MockLayer,
  Rect: MockRect,
  Circle: MockCircle,
  Line: MockLine,
  Group: MockGroup,
  Image: MockImage,
  Transformer: MockTransformer,
};

export default Konva;
