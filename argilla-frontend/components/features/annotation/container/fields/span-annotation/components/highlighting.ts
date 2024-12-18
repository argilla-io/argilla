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
    delete(className: string): void;
    entries(): [string, Highlight][];
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

const isCSSHighlightsSupported = !!CSS.highlights;

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
      removeSpan: (span: Span) => void,
      replaceEntity: (entity: Entity) => void,
      cloneSpanWith: (span: Span, entity: Entity) => void
    ) => Element,
    config?: InitialConfiguration,
    styles?: Styles
  ) {
    this.styles = {
      entitiesGap: 16,
      lineHeight: config.allowOverlap ? 48 : 32,
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

  get nodeSpans() {
    return this.spans.filter((s) => s.node.id === this.nodeId);
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
    if (!isCSSHighlightsSupported) {
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

    this.showPreSelection();
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
    const maxOverlappedLevels = this.nodeSpans.reduce(
      (max, span) => Math.max(max, span.overlap.level),
      0
    );

    const lineHeight =
      maxOverlappedLevels > 2
        ? this.styles.lineHeight +
          this.styles.entitiesGap * Math.max(0, maxOverlappedLevels - 2)
        : this.styles.lineHeight;

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
      this.showSelection();

      this.showPreSelection();
    });

    new ResizeObserver(() => this.applyStyles()).observe(node);

    this.applyStylesOnScroll();
  }

  private scroll = () => {
    this.applyEntityStyle();
  };

  private showSelection() {
    if (!this.entity) return;

    const className = `${this.styles.entityCssKey}-${this.entity.id}-selection`;

    const selection = this.createTextSelection();

    if (!selection) {
      return CSS.highlights.delete(className);
    }

    if (selection?.node.id !== this.nodeId) return;

    const range = this.createRange(selection);

    if (!range) return;

    CSS.highlights.set(className, new Highlight(range));
  }

  private showPreSelection() {
    if (!this.entity) return;

    const tokenizedClassName = `${this.styles.entityCssKey}-${this.entity.id}-pre-selection`;

    const selection = this.createTextSelection();

    if (!selection) {
      return CSS.highlights.delete(tokenizedClassName);
    }

    if (selection.node.id !== this.nodeId) return;

    const simulatedSpan = this.spanSelection.crateSpan(selection, this.config);

    if (!simulatedSpan) return;

    const firstRange = this.createRange({
      ...simulatedSpan,
      from: simulatedSpan.from,
      to: selection.from,
    });

    const lastRange = this.createRange({
      ...simulatedSpan,
      from: selection.to,
      to: simulatedSpan.to,
    });

    if (!firstRange || !lastRange) return;

    CSS.highlights.set(
      tokenizedClassName,
      new Highlight(firstRange, lastRange)
    );
  }

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
    const textSelection = this.createTextSelection(true);
    this.spanSelection.addSpan(textSelection, this.config);
  }

  private getSelectedText() {
    if (window.getSelection) {
      return window.getSelection();
    }
  }

  private applyStyles() {
    if (!isCSSHighlightsSupported) return;

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

    const entityCssKey = this.styles.entityCssKey;
    for (const [key] of CSS.highlights.entries()) {
      if (key.startsWith(entityCssKey)) CSS.highlights.delete(key);
    }

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

    for (const span of this.nodeSpans) {
      const entityPosition = this.createPosition(span);

      const entityElement = this.EntityComponentConstructor(
        span,
        entityPosition,
        (isHovered) => this.hoverSpan(span, isHovered),
        (span) => this.removeSpan(span),
        (newEntity) => this.replaceEntity(span, newEntity),
        (span, newEntity) => this.addSpanBaseOn(span, newEntity)
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
      baseEntityGap: this.styles.entitiesGap,
    };
  }

  private removeSpan(span: Span) {
    this.spanSelection.removeSpan(span);

    this.applyStyles();
  }

  public createRange({ from, to, node }: Span) {
    try {
      const range = new Range();

      range.setStart(node.element, from);
      range.setEnd(node.element, to);

      return range;
    } catch {}
  }

  private createTextSelection(clear = false): TextSelection | undefined {
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

    if (clear) selection.empty();

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
