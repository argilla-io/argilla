import { type Span, type TextSelection, SpanSelection } from "./span-selection";

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

  /** This class name is used to style the entity span */
  entityClassName?: string;

  /** Span container ID */
  spanContainerId?: string;
};

export class Highlighting {
  private readonly spanSelection = SpanSelection.getInstance();
  private node: HTMLElement | undefined;
  private readonly styles: Required<Styles>;
  entity = "";

  constructor(
    private readonly nodeId: string,
    private readonly entities: string[],
    styles: Styles
  ) {
    const entitiesCSS = entities.reduce((acc, entity) => {
      acc[entity] = `hl-${entity}`;

      return acc;
    }, {});

    this.styles = {
      entitiesGap: 8,
      entityClassName: "",
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

  private attachNode(node: HTMLElement) {
    this.node = node;
    document.body.appendChild(this.entitySpanContainer);

    this.node.addEventListener("mouseup", () => {
      this.highlightUserSelection();

      this.applyStyles();
    });

    window.addEventListener("resize", () => {
      this.applyEntityStyle();

      this.applyStylesOnScroll();
    });

    this.applyStylesOnScroll();
  }

  private applyStylesOnScroll() {
    const scroll = this.getScrollParent(this.node);

    scroll?.removeEventListener("scroll", () => {
      this.applyEntityStyle();
    });

    scroll?.addEventListener("scroll", () => {
      this.applyEntityStyle();
    });
  }

  mount() {
    const node = document.getElementById(this.nodeId)!;

    if (!node) throw new Error(`Node with id ${this.nodeId} not found`);

    this.attachNode(node);
  }

  unmount() {
    this.removeAllHighlights();
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

  replaceEntity(span: Span, entity: string) {
    this.spanSelection.replaceEntity(span, entity);
    this.applyStyles();
  }

  removeAllHighlights() {
    this.spanSelection.clear();
    this.applyStyles();
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
      if (!highlights[span.entity]) highlights[span.entity] = [];

      const range = this.createRange(span);

      highlights[span.entity].push(range);
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

    for (const span of this.spans) {
      const { entity } = span;
      const range = this.createRange({ ...span, to: span.from + 1 });
      const { left, top } = range.getBoundingClientRect();

      const position = { left, top: top + window.scrollY };

      if (overlappedSpans.some((p) => p.left === left && p.top === top)) {
        position.top += this.styles.entitiesGap;
      }

      const entityElement = document.createElement("span");
      entityElement.className = this.styles.entityClassName;

      entityElement.style.left = `${position.left}px`;
      entityElement.style.top = `${position.top}px`;

      entityElement.innerText = entity;

      const button = document.createElement("span");
      button.innerText = " - X ";
      button.style.cursor = "pointer";
      button.onclick = () => {
        this.removeSpan(span);
      };

      entityElement.appendChild(button);

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
