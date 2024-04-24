import {
  type Span,
  type TextSelection,
  type Entity,
  SpanSelection,
  Configuration,
  OverlappedSpan,
} from "./span-selection";

export type LoadedSpan = Omit<Span, "text" | "node">;

export type Position = {
  top: number;
  left: number;
  width: number;
  topEnd: number;
  right: number;
  lineHeight: number;
};

declare class Highlight {
  constructor(...ranges: Range[]);
}

declare namespace CSS {
  const highlights: {
    set(className: string, highlight: Highlight): void;
    clear(): void;
  };
}

type Dictionary<V> = {
  [key: string]: V;
};

type Styles = {
  /** Is the Highlight CSS class name for each entity, commonly would be 'hl' */
  entityCssKey?: string;

  /** This gap is used to separate spans vertically when allow overlap is true */
  entitiesGap?: number;

  /** Span container ID */
  spanContainerId?: string;

  /** Overlap line height */
  lineHeight: number;
};

type InitialConfiguration = Partial<Omit<Configuration, "lineHeight">>;

export class Highlighting {
  private readonly spanSelection = SpanSelection.getInstance();
  private node: HTMLElement | undefined;
  private readonly styles: Required<Styles>;
  private entity: Entity = null;
  private scrollingElement: HTMLElement;
  readonly config: Configuration;

  constructor(
    private readonly nodeId: string,
    private readonly EntityComponentConstructor: (
      span: Span,
      entityPosition: Position,
      hoverSpan: (value: boolean) => void,
      removeSpan: () => void,
      replaceEntity: (entity: Entity) => void,
      cloneSpanWith: (entity: Entity) => void
    ) => Element,
    config?: InitialConfiguration,
    styles?: Styles
  ) {
    this.styles = {
      entitiesGap: 16,
      lineHeight: 32,
      spanContainerId: `entity-span-container-${nodeId}`,
      entityCssKey: "hl",
      ...styles,
    };

    this.config = {
      allowOverlap: false,
      allowCharacter: false,
      lineHeight: this.styles.lineHeight,
      ...config,
    };
  }

  get spans() {
    return [...this.spanSelection.spans];
  }

  private get entitySpanContainer() {
    const { spanContainerId } = this.styles;

    let node = document.getElementById(spanContainerId);
    if (!node) {
      node = document.createElement("div");
      node.id = spanContainerId;
    }

    return node;
  }

  mount(selections: LoadedSpan[] = []) {
    if (!CSS.highlights) {
      throw new Error(
        "The CSS Custom Highlight API is not supported in this browser!"
      );
    }

    const node = document.getElementById(this.nodeId)!;

    if (!node) throw new Error(`Node with id ${this.nodeId} not found`);

    this.attachNode(node);

    this.loadHighlights(selections);
  }

  unmount() {
    this.removeAllHighlights();
  }

  changeSelectedEntity(entity: Entity) {
    this.entity = entity;
  }

  allowCharacterAnnotation(allow: boolean) {
    this.config.allowCharacter = allow;
  }

  replaceEntity(span: Span, entity: Entity) {
    this.spanSelection.replaceEntity(span, entity);
    this.applyStyles();
  }

  removeAllHighlights() {
    this.spanSelection.clear();
    this.applyStyles();
  }

  private loadHighlights(selections: LoadedSpan[]) {
    if (!this.node) {
      throw new Error(
        "Node not attached, use `attachNode` method with HTMLElement that contains the text to select"
      );
    }

    const loaded: Omit<Span, "overlap">[] = selections.map((s) => ({
      ...s,
      text: "",
      node: {
        element: this.node.firstChild,
        id: this.nodeId,
      },
    }));

    this.spanSelection.loadSpans(loaded);

    this.applyStyles();
  }

  private updateLineHeight() {
    const maxOverlappedLevels = this.spans.reduce(
      (max, span) => Math.max(max, span.overlap.level),
      0
    );

    const lineHeight =
      this.styles.lineHeight +
      this.styles.entitiesGap * Math.max(0, maxOverlappedLevels - 1);

    this.config.lineHeight = lineHeight;
  }

  private attachNode(node: HTMLElement) {
    this.node = node;
    const nodeParent = node.parentNode;
    nodeParent.appendChild(this.entitySpanContainer.cloneNode(true));

    this.node.addEventListener("click", () => {
      this.highlightUserSelection();

      this.applyStyles();
    });

    document.addEventListener("selectionchange", () => {
      const selection = document.getSelection();
      if (selection.rangeCount === 0) return;

      const range = selection.getRangeAt(0);

      if (!range) return;

      const entity = this.entity;
      const styles = this.styles;

      const isSelectionInsideNode =
        range?.startContainer?.parentNode instanceof Element &&
        range?.startContainer?.parentNode.id === this.nodeId;

      if (entity && isSelectionInsideNode) {
        const className = `${styles.entityCssKey}-${entity.id}-selection`;

        CSS.highlights.set(className, new Highlight(range));
      }
    });

    new ResizeObserver(() => this.applyStyles()).observe(node);

    this.applyStylesOnScroll();
  }

  private scroll = () => {
    this.applyEntityStyle();
  };

  private applyStylesOnScroll() {
    if (this.scrollingElement) {
      this.scrollingElement.removeEventListener("scroll", this.scroll);
    }

    this.scrollingElement = this.getScrollParent(this.entitySpanContainer);

    if (!this.scrollingElement) return;

    this.scrollingElement.removeEventListener("scroll", this.scroll);

    this.scrollingElement?.addEventListener("scroll", this.scroll);
  }

  private highlightUserSelection() {
    const textSelection = this.createTextSelection();
    this.spanSelection.addSpan(textSelection, this.config);
  }

  private getSelectedText() {
    if (window.getSelection) {
      return window.getSelection();
    }
  }

  private applyStyles() {
    if (!CSS.highlights) return;

    this.applyHighlightStyle();
    this.applyEntityStyle();
  }

  private applyHighlightStyle(
    getClassName: (span: Span) => string = (span) =>
      `${this.styles.entityCssKey}-${span.entity.id}`
  ) {
    const highlights: Dictionary<Range[]> = {};

    for (const span of this.spans) {
      const className = getClassName(span);

      if (!highlights[className]) highlights[className] = [];

      const range = this.createRange(span);

      highlights[className].push(range);
    }

    CSS.highlights.clear();

    for (const [entity, selections] of Object.entries(highlights)) {
      CSS.highlights.set(entity, new Highlight(...selections.flat()));
    }
  }

  private hoverSpan(hoveredSpan: Span, isHovered: boolean) {
    this.applyHighlightStyle((span) =>
      hoveredSpan === span && isHovered
        ? `${this.styles.entityCssKey}-${span.entity.id}-hover`
        : `${this.styles.entityCssKey}-${span.entity.id}`
    );
  }

  private applyEntityStyle() {
    while (this.entitySpanContainer.firstChild) {
      this.entitySpanContainer.removeChild(this.entitySpanContainer.firstChild);
    }

    this.updateLineHeight();

    for (const span of this.spans) {
      const { node } = span;

      if (node.id !== this.nodeId) continue;

      const entityPosition = this.createPosition(span);

      const entityElement = this.EntityComponentConstructor(
        span,
        entityPosition,
        (isHovered) => this.hoverSpan(span, isHovered),
        () => this.removeSpan(span),
        (newEntity) => this.replaceEntity(span, newEntity),
        (newEntity) => this.addSpanBaseOn(span, newEntity)
      );

      this.entitySpanContainer.appendChild(entityElement);
    }
  }

  addSpanBaseOn(span: Span, newEntity: Entity) {
    if (span.entity.id === newEntity.id) return;

    const clonedSpan = {
      ...span,
      entity: newEntity,
    };

    this.spanSelection.select(clonedSpan);

    this.applyStyles();
  }

  private createPosition(span: OverlappedSpan) {
    const rangePositionStart = this.createRange({
      ...span,
      to: span.from + 1,
    }).getBoundingClientRect();
    const rangePositionEnd = this.createRange({
      ...span,
      from: span.to - 1,
    }).getBoundingClientRect();

    const rangeNaturalPosition = this.createRange(span).getBoundingClientRect();

    const offset = this.entitySpanContainer.getBoundingClientRect();
    const scrollTop = this.entitySpanContainer.scrollTop;

    const { left, top } = rangePositionStart;
    const { right, top: topEnd } = rangePositionEnd;
    const { width } = rangeNaturalPosition;

    const position = {
      left,
      top: top + window.scrollY + this.styles.entitiesGap / 10,
      width,
      right: right + window.scrollX,
      topEnd: topEnd + window.scrollY,
    };

    if (span.overlap.level > 0) {
      position.top += this.styles.entitiesGap * span.overlap.index;
      position.topEnd += this.styles.entitiesGap * span.overlap.index;
    }

    return {
      top: position.top - offset.top + scrollTop,
      left: position.left - offset.left,
      width: position.width,
      topEnd: position.topEnd - offset.top + scrollTop,
      right: position.right - offset.left,
      lineHeight: this.config.lineHeight,
    };
  }

  private removeSpan(span: Span) {
    this.spanSelection.removeSpan(span);

    const spans = this.spans;

    this.removeAllHighlights();

    this.loadHighlights(spans);
  }

  public createRange({ from, to, node }: Span) {
    const range = new Range();

    range.setStart(node.element, from);
    range.setEnd(node.element, to);

    return range;
  }

  private createTextSelection(): TextSelection | undefined {
    const selection = this.getSelectedText();
    if (selection?.type !== "Range" || !this.entity) return;

    const text = selection.toString();
    const from = selection.anchorOffset;
    const to = selection.focusOffset;

    const textSelection = {
      from: Math.min(from, to),
      to: Math.max(from, to),
      text,
      entity: this.entity,
      node: {
        id: this.nodeId,
        element: selection.focusNode,
        text: selection.focusNode.textContent,
      },
    };

    selection.empty();

    return textSelection;
  }

  private getScrollParent(node) {
    if (node == null) {
      return null;
    }

    if (node.scrollHeight > node.clientHeight) return node;

    return this.getScrollParent(node.parentNode);
  }
}
