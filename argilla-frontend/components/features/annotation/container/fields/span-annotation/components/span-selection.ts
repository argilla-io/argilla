export type Entity = {
  id: string;
};

export type TextSelection = {
  from: number;
  to: number;
  entity: Entity;
  text: string;
  node: {
    element: Node;
    text: string;
    id: string;
  };
};

export type Span = {
  from: number;
  to: number;
  entity: Entity;
  text: string;
  node: {
    element: Node;
    id: string;
  };
};

export type OverlappedSpan = Span & {
  overlap: {
    level: number;
    index: number;
  };
};

export type Configuration = {
  allowOverlap: boolean;
  allowCharacter: boolean;
  lineHeight: number;
};

export class SpanSelection {
  private selections: OverlappedSpan[] = [];

  protected constructor() {}

  // eslint-disable-next-line no-use-before-define
  private static instance: SpanSelection;
  public static getInstance() {
    if (!this.instance) {
      this.instance = new SpanSelection();
    }

    return this.instance;
  }

  get spans() {
    return [...this.selections];
  }

  crateSpan(
    selection?: TextSelection,
    config?: Configuration
  ): Span | undefined {
    if (!selection) return;
    if (this.isOutOfRange(selection)) return;

    const newSelection = { ...selection };

    if (!config?.allowCharacter) {
      if (this.isEmpty(newSelection.text)) return;

      this.completeLeftSide(newSelection);

      this.completeRightSide(newSelection);
    }

    const { from, to, entity, text, node } = newSelection;

    const span = {
      from,
      to,
      entity,
      text,
      node: {
        element: node.element,
        id: node.id,
      },
    };

    return span;
  }

  addSpan(selection?: TextSelection, config?: Configuration) {
    const span = this.crateSpan(selection, config);

    if (!span) return;

    const filteredSelections = this.selections.filter(
      (s) => s.node.id === span.node.id
    );

    const overlaps = this.selections.filter((s) => {
      return (
        (span.from <= s.from && span.to >= s.to) ||
        (span.from >= s.from && span.to <= s.to) ||
        (span.from < s.from && span.to > s.from) ||
        (span.from < s.to && span.to > s.to)
      );
    });

    if (!config?.allowOverlap) {
      this.selections = [
        ...this.selections.filter((s) => s.node.id !== span.node.id),
        ...filteredSelections.filter((s) => !overlaps.includes(s)),
      ];
    }

    this.select(span);
  }

  select(selected: Span) {
    if (this.exists(selected)) return;

    this.completeOutOfBoundaries(selected);

    const overlaps = this.selections
      .filter((s) => s.node.id === selected.node.id)
      .filter((s) => {
        return (
          (selected.from <= s.from && selected.to >= s.to) ||
          (selected.from >= s.from && selected.to <= s.to) ||
          (selected.from < s.from && selected.to > s.from) ||
          (selected.from < s.to && selected.to > s.to)
        );
      });

    const maxLevelInOverlaps =
      overlaps.reduce((acc, curr) => Math.max(acc, curr.overlap.level), 0) + 1;

    const newVariable = {
      ...selected,
      overlap: {
        level: maxLevelInOverlaps,
        index: maxLevelInOverlaps - 1,
      },
    };

    this.selections.push(newVariable);
  }

  loadSpans(selections: Span[]) {
    selections.forEach((s) => this.select(s));
  }

  replaceEntity(span: Span, entity: Entity) {
    const found = this.selections.find(
      (s) => this.createId(s) === this.createId(span)
    );

    if (!found) return;

    found.entity = entity;
  }

  clear() {
    this.selections = [];
  }

  removeSpan(span: Span) {
    this.remove(span);

    const nodeSpans = this.spans.filter((s) => s.node.id === span.node.id);

    nodeSpans.forEach((span) => {
      this.remove(span);
    });

    this.loadSpans(nodeSpans);
  }

  private remove(span: Span) {
    this.selections = this.selections.filter(
      (s) => this.createId(s) !== this.createId(span)
    );
  }

  private completeOutOfBoundaries(selected: Span) {
    selected.from = Math.max(0, selected.from);
    selected.to = Math.min(
      selected.node.element.textContent.length,
      selected.to
    );
  }

  private isOutOfRange(selection: TextSelection) {
    return selection.from < 0 || selection.to < 0;
  }

  private exists(span: Span) {
    return this.selections.some(
      (s) => this.createId(s) === this.createId(span)
    );
  }

  private completeLeftSide(selection: TextSelection) {
    while (true) {
      const prevChar = selection.node.text.charAt(selection.from - 1);

      if (
        this.isEmpty(prevChar) ||
        this.isSymbol(prevChar) ||
        selection.to === 0
      ) {
        break;
      }

      const firstCharacter = selection.text.charAt(0);

      if (this.isEmpty(firstCharacter)) {
        selection.from++;
        selection.text = selection.text.slice(1);
        break;
      }

      selection.from--;
      selection.text = `${prevChar}${selection.text}`;
    }
  }

  private completeRightSide(selection: TextSelection) {
    while (true) {
      const nextCharacter = selection.node.text.charAt(selection.to);

      if (
        this.isEmpty(nextCharacter) ||
        this.isSymbol(nextCharacter) ||
        selection.to === selection.node.text.length
      ) {
        break;
      }

      const lastCharacter = selection.text.charAt(selection.text.length - 1);

      if (this.isEmpty(lastCharacter)) {
        selection.to--;
        selection.text = selection.text.slice(0, -1);
        break;
      }

      selection.to++;
      selection.text = `${selection.text}${nextCharacter}`;
    }
  }

  private isEmpty(character: string) {
    return character === " " || character === "\n";
  }

  private isSymbol(character: string) {
    const numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];

    return (
      !numbers.includes(character) &&
      character.toLowerCase() === character.toUpperCase()
    );
  }

  private createId(span: Span | TextSelection) {
    return `${span.from}-${span.to}-${span.entity.id}-${span.node.id}`;
  }
}
