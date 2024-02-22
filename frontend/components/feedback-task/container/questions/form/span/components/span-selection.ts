export type TextSelection = {
  from: number;
  to: number;
  entity: string;
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
  entity: string;
  text: string;
  node: {
    element: Node;
    id: string;
  };
};

type Configuration = {
  allowOverlap: boolean;
  allowCharacter: boolean;
};

export class SpanSelection {
  private selections: Span[] = [];

  private constructor() {}

  // eslint-disable-next-line no-use-before-define
  private static instance: SpanSelection;
  public static getInstance() {
    if (!SpanSelection.instance) {
      SpanSelection.instance = new SpanSelection();
    }

    return SpanSelection.instance;
  }

  get spans() {
    return [...this.selections];
  }

  config: Configuration = {
    allowOverlap: false,
    allowCharacter: false,
  };

  public addSpan(selection?: TextSelection) {
    if (!selection) return;
    if (this.isOutOfRange(selection)) return;

    const filteredSelections = this.selections.filter(
      (s) => s.node.id === selection.node.id
    );

    if (!this.config.allowCharacter) {
      if (this.isEmpty(selection.text)) return;

      this.completeLeftSide(selection);

      this.completeRightSide(selection);
    }

    if (!this.config.allowOverlap) {
      const overlaps = this.selections.filter((s) => {
        return (
          (selection.from <= s.from && selection.to >= s.to) ||
          (selection.from >= s.from && selection.to <= s.to) ||
          (selection.from < s.from && selection.to > s.from) ||
          (selection.from < s.to && selection.to > s.to)
        );
      });

      this.selections = [
        ...this.selections.filter((s) => s.node.id !== selection.node.id),
        ...filteredSelections.filter((s) => !overlaps.includes(s)),
      ];
    }

    if (this.exists(selection)) return;

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

  isOutOfRange(selection: TextSelection) {
    return selection.from <= 0 || selection.to <= 0;
  }

  loadSpans(selections: Span[]) {
    selections.forEach((s) => this.select(s));
  }

  replaceEntity(span: Span, entity: string) {
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

  private exists(selection: TextSelection) {
    return this.selections.some(
      (s) => this.createId(s) === this.createId(selection)
    );
  }

  private select(selected: Span) {
    this.selections.push(selected);
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
    return `${span.from}-${span.to}-${span.entity}-${span.node.id}`;
  }
}
