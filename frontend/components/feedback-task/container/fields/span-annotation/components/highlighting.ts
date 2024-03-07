import {
  type Span,
  type TextSelection,
  type Entity,
  SpanSelection,
  Configuration,
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
  private readonly entitiesCSS: {};

  constructor(
    private readonly nodeId: string,
    entities: Omit<Entity, "className">[],
    private readonly EntityComponentConstructor: (
      selectedEntity: Entity,
      entityPosition: Position,
      removeSpan: () => void,
      replaceEntity: (entity: Entity) => void
    ) => Element,
    styles: Styles & { entitiesCSS?: Dictionary<string> }
  ) {
    this.entitiesCSS =
      styles.entitiesCSS ??
      entities.reduce((acc, entity) => {
        acc[entity.id] = `hl-${entity.id}`;

        return acc;
      }, {});

    this.styles = {
      entitiesGap: 8,
      spanContainerId: `entity-span-container-${nodeId}`,
      ...styles,
    };
  }

  config: Configuration = {
    allowOverlap: false,
    allowCharacter: false,
  };

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

  mount(selections: any[] = []) {
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

  private loadHighlights(selections: Omit<Span, "text" | "node">[] = []) {
    if (!this.node) {
      throw new Error(
        "Node not attached, use `attachNode` method with HTMLElement that contains the text to select"
      );
    }

    const loaded: Span[] = selections.map((s) => ({
      ...s,
      entity: {
        ...s.entity,
        className: this.entitiesCSS[s.entity.id],
      },
      text: "",
      node: {
        element: this.node.firstChild,
        id: this.nodeId,
      },
    }));

    this.spanSelection.loadSpans(loaded);

    this.applyStyles();
  }

  allowCharacterAnnotation(value: boolean) {
    this.config.allowCharacter = value;
  }

  replaceEntity(span: Span, entity: Entity) {
    this.spanSelection.replaceEntity(span, {
      ...entity,
      className: this.entitiesCSS[entity.id],
    });
    this.applyStyles();
  }

  removeAllHighlights() {
    this.spanSelection.clear();
    this.applyStyles();
  }

  private attachNode(node: HTMLElement) {
    this.node = node;
    const nodeParent = node.parentNode;
    nodeParent.appendChild(this.entitySpanContainer.cloneNode(true));

    this.node.addEventListener("click", () => {
      this.highlightUserSelection();

      this.applyStyles();
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

  private applyHighlightStyle() {
    CSS.highlights.clear();
    const highlights: Dictionary<Range[]> = {};

    for (const span of this.spans) {
      const className = span.entity.className;

      if (!highlights[className]) highlights[className] = [];

      const range = this.createRange(span);

      highlights[className].push(range);
    }

    for (const [entity, selections] of Object.entries(highlights)) {
      CSS.highlights.set(entity, new Highlight(...selections.flat()));
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
      const { entity, node } = span;

      if (node.id !== this.nodeId) continue;

      const rangePosition = this.createRange({
        ...span,
        to: span.from + 1,
      }).getBoundingClientRect();
      const rangeWidth = this.createRange(span).getBoundingClientRect();
      const offset = this.entitySpanContainer.getBoundingClientRect();
      const scrollTop = this.entitySpanContainer.scrollTop;

      const { left, top } = rangePosition;
      const { width } = rangeWidth;

      const position = { left, top: top + window.scrollY, width };

      if (overlappedSpans.some((p) => p.left === left && p.top === top)) {
        position.top += this.styles.entitiesGap;
      }

      const entityPosition = {
        top: `${position.top - offset.top + scrollTop}px`,
        left: `${position.left - offset.left}px`,
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
      entity: {
        ...this.entity,
        className: this.entitiesCSS[this.entity.id],
      },
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
