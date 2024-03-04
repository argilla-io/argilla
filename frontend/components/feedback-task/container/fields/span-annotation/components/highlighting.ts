import {
  type Span,
  type TextSelection,
  type Entity,
  SpanSelection,
} from "./span-selection";

export type Position = { top: string; left: string };

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
  /** Is the Highlight CSS class name for each entity */
  entitiesCSS?: Dictionary<string>;

  /** This gap is used to separate spans vertically when allow overlap is true */
  entitiesGap?: number;

  /** Span container ID */
  spanContainerId?: string;
};

export class Highlighting {
  private readonly spanSelection = SpanSelection.getInstance();
  private node: HTMLElement | undefined;
  private readonly styles: Required<Styles>;
  private entity: Entity = null;

  private scrollingElement: HTMLElement;

  constructor(
    private readonly nodeId: string,
    private readonly entities: Entity[],
    private readonly EntityComponentConstructor: (
      selectedEntity: Entity,
      entityPosition: Position,
      removeSpan: () => void,
      replaceEntity: (entity: Entity) => void
    ) => Element,
    styles: Styles
  ) {
    const entitiesCSS = entities.reduce((acc, entity) => {
      acc[entity.id] = `hl-${entity.id}`;

      return acc;
    }, {});

    this.styles = {
      entitiesGap: 8,
      spanContainerId: "entity-span-container",
      entitiesCSS,
      ...styles,
    };
  }

  get spans() {
    return [...this.spanSelection.spans];
  }

  get config() {
    return this.spanSelection.config;
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

  mount() {
    const node = document.getElementById(this.nodeId)!;

    if (!node) throw new Error(`Node with id ${this.nodeId} not found`);

    this.attachNode(node);
  }

  unmount() {
    this.removeAllHighlights();
  }

  changeSelectedEntity(entity: Entity) {
    this.entity = entity;
  }

  loadHighlights(selections: Span[] = []) {
    if (!CSS.highlights) {
      throw new Error(
        "The CSS Custom Highlight API is not supported in this browser!"
      );
    }

    if (!this.node) {
      throw new Error(
        "Node not attached, use `attachNode` method with HTMLElement that contains the text to select"
      );
    }

    this.spanSelection.loadSpans(selections);

    this.applyStyles();
  }

  allowCharacterAnnotation(value: boolean) {
    this.spanSelection.config.allowCharacter = value;
  }

  replaceEntity(span: Span, entity: Entity) {
    this.spanSelection.replaceEntity(span, entity);
    this.applyStyles();
  }

  removeAllHighlights() {
    this.spanSelection.clear();
    this.applyStyles();
  }

  private attachNode(node: HTMLElement) {
    this.node = node;
    const nodeParent = this.getScrollParent(node) || node.parentNode;
    nodeParent.appendChild(this.entitySpanContainer);

    this.node.addEventListener("mouseup", () => {
      this.highlightUserSelection();

      this.applyStyles();
    });

    new ResizeObserver(() => updateStyles()).observe(node);

    const updateStyles = () => {
      this.applyEntityStyle();
      this.applyStylesOnScroll();
    };

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
    this.spanSelection.addSpan(textSelection);
  }

  private getSelectedText() {
    if (window.getSelection) {
      return window.getSelection();
    }
  }

  private applyStyles() {
    this.applyHighlightStyle();
    this.applyEntityStyle();
  }

  private applyHighlightStyle() {
    CSS.highlights.clear();
    const highlights: Dictionary<Range[]> = {};

    for (const span of this.spans) {
      if (!highlights[span.entity.id]) highlights[span.entity.id] = [];

      const range = this.createRange(span);

      highlights[span.entity.id].push(range);
    }

    for (const highlight of Object.entries(highlights)) {
      const [entity, selections] = highlight;
      const { entitiesCSS } = this.styles;
      const className = entitiesCSS[entity as keyof typeof entitiesCSS];

      CSS.highlights.set(className, new Highlight(...selections.flat()));
    }
  }

  private applyEntityStyle() {
    const overlappedSpans: {
      left: number;
      top: number;
    }[] = [];

    while (this.entitySpanContainer.firstChild) {
      this.entitySpanContainer.removeChild(this.entitySpanContainer.firstChild);
    }

    const parent =
      this.getScrollParent(this.entitySpanContainer) ||
      this.entitySpanContainer.parentNode;

    for (const span of this.spans) {
      const { entity } = span;
      const rangePosition = this.createRange({
        ...span,
        to: span.from + 1,
      }).getBoundingClientRect();
      const rangeWidth = this.createRange(span).getBoundingClientRect();
      const parentOffset = parent.getBoundingClientRect();
      const parentScrollTop = parent.scrollTop;

      const { left, top } = rangePosition;
      const { width } = rangeWidth;

      const position = { left, top: top + window.scrollY, width };

      if (overlappedSpans.some((p) => p.left === left && p.top === top)) {
        position.top += this.styles.entitiesGap;
      }

      const entityPosition = {
        top: `${position.top - parentOffset.top + parentScrollTop}px`,
        left: `${position.left - parentOffset.left}px`,
        width: `${position.width}px`,
      };

      const entityElement = this.EntityComponentConstructor(
        entity,
        entityPosition,
        () => this.removeSpan(span),
        (newEntity: Entity) => this.replaceEntity(span, newEntity)
      );

      this.entitySpanContainer.appendChild(entityElement);

      overlappedSpans.push(position);
    }
  }

  private removeSpan(span: Span) {
    this.spanSelection.removeSpan(span);
    this.applyStyles();
  }

  private createRange({ from, to, node }: Span) {
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
