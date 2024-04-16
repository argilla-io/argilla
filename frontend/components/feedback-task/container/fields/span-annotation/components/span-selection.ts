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

  addSpan(selection?: TextSelection, config?: Configuration) {
    if (!selection) return;
    if (this.isOutOfRange(selection)) return;

    const filteredSelections = this.selections.filter(
      (s) => s.node.id === selection.node.id
    );

    if (!config?.allowCharacter) {
      if (this.isEmpty(selection.text)) return;

      this.completeLeftSide(selection);

      this.completeRightSide(selection);
    }

    const overlaps = this.selections.filter((s) => {
      return (
        (selection.from <= s.from && selection.to >= s.to) ||
        (selection.from >= s.from && selection.to <= s.to) ||
        (selection.from < s.from && selection.to > s.from) ||
        (selection.from < s.to && selection.to > s.to)
      );
    });

    if (!config?.allowOverlap) {
      this.selections = [
        ...this.selections.filter((s) => s.node.id !== selection.node.id),
        ...filteredSelections.filter((s) => !overlaps.includes(s)),
      ];
    }

    const { from, to, entity, text, node } = selection;

    this.select({
      from,
      to,
      entity,
      text,
      node: {
        element: node.element,
        id: node.id,
      },
    });
  }

  select(selected: Span) {
    if (this.exists(selected)) return;

    this.completeOutOfBoundaries(selected);

    const overlaps = this.selections.filter((s) => {
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
        selection.to === selection.node.text.length - 1
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
