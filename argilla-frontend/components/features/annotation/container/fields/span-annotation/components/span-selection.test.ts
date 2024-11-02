/* eslint-disable quotes */
import {
  Configuration,
  OverlappedSpan,
  SpanSelection as SpanSelectionBase,
  TextSelection,
} from "./span-selection";

class SpanSelection extends SpanSelectionBase {
  config: Configuration = {
    allowCharacter: false,
    allowOverlap: false,
    lineHeight: 32,
  };

  public constructor() {
    super();
  }

  public addSpan(span: TextSelection): void {
    super.addSpan(span, this.config);
  }
}

const DUMMY_TEXT = `What is Lorem Ipsum? Lorem Ipsum is simply dummy text of the printing and
      typesetting industry. Lorem Ipsum has been the industry's standard dummy
      text ever since the 1500s, when an unknown printer took a galley of type
      and scrambled it to make a type specimen book. It has survived not only
      five centuries, but also the leap into electronic typesetting, remaining
      essentially unchanged. It was popularised in the 1960s with the release of
      Letraset sheets containing Lorem Ipsum passages, and more recently with
      desktop publishing software like Aldus PageMaker including versions of
      Lorem Ipsum. Why do we use it? It is a long established fact that a reader
      will be distracted by the readable content of a page when looking at its
      layout. The point of using Lorem Ipsum is that it has a more-or-less
      normal distribution of letters, as opposed to using 'Content here, content
      here', making it look like readable English. Many desktop publishing
      packages and web page editors now use Lorem Ipsum as their default model
      text, and a search for 'lorem ipsum' will uncover many web sites still in
      their infancy. Various versions have evolved over the years, sometimes by
      accident, sometimes on purpose (injected humour and the like). Where does
      it come from? Contrary to popular belief, Lorem Ipsum is not simply random
      text. It has roots in a piece of classical Latin literature from 45 BC,
      making it over 2000 years old. Richard McClintock, a Latin professor at
      Hampden-Sydney College in Virginia, looked up one of the more obscure
      Latin words, consectetur, from a Lorem Ipsum passage, and going through
      the cites of the word in classical literature, discovered the undoubtable
      source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus
      Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in
      45 BC. This book is a treatise on the theory of ethics, very popular
      during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor
      sit amet..", comes from a line in section 1.10.32. The standard chunk of
      Lorem Ipsum used since the 1500s is reproduced below for those interested.
      Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum et Malorum" by
      Cicero are also reproduced in their exact original form, accompanied by
      English versions from the 1914 translation by H. Rackham.`;

const ISSUES = {
  NOT_SELECTING_WHOLE_WORD: "Apple10dollars",
};

type TestSelection = {
  from: number;
  to: number;
  text: string;
  entity: string;
};

const node = {
  textContent: DUMMY_TEXT,
} as HTMLElement;

const createTextSelection = (
  selection: TestSelection,
  nodeSelecting: HTMLElement = node
): TextSelection => {
  return {
    from: selection.from,
    to: selection.to,
    text: selection.text,
    entity: {
      id: selection.entity,
    },
    node: {
      element: nodeSelecting,
      id: "node-id",
      text: nodeSelecting.textContent,
    },
  };
};

const createSpan = (
  selection: TestSelection & { level?: number },
  nodeSelecting: HTMLElement = node
): OverlappedSpan => {
  const level = selection.level || 1;

  return {
    from: selection.from,
    to: selection.to,
    text: selection.text,
    entity: {
      id: selection.entity,
    },
    node: {
      element: nodeSelecting,
      id: "node-id",
    },
    overlap: {
      level,
      index: level - 1,
    },
  };
};

describe("Span Selection", () => {
  describe("addSpan", () => {
    describe("should auto complete token correctly", () => {
      test.each([
        [
          { from: 9, to: 15, text: "orem I", entity: "TOKEN" },
          {
            from: 8,
            to: 19,
            text: "Lorem Ipsum",
            entity: "TOKEN",
          },
        ],
        [
          { from: 852, to: 854, text: "or", entity: "TOKEN" },
          { from: 852, to: 854, text: "or", entity: "TOKEN" },
        ],
        [
          { from: 5, to: 8, text: "is ", entity: "TOKEN" },
          { from: 5, to: 7, text: "is", entity: "TOKEN" },
        ],
        [
          { from: 5, to: 9, text: "is L", entity: "TOKEN" },
          { from: 5, to: 13, text: "is Lorem", entity: "TOKEN" },
        ],
        [
          { from: 7, to: 10, text: " Lo", entity: "TOKEN" },
          { from: 8, to: 13, text: "Lorem", entity: "TOKEN" },
        ],
        [
          { from: 8, to: 20, text: "Lorem Ipsum?", entity: "TOKEN" },
          {
            from: 8,
            to: 20,
            text: "Lorem Ipsum?",
            entity: "TOKEN",
          },
        ],
        [
          {
            from: 1865,
            to: 1870,
            text: ".10.3",
            entity: "TOKEN",
          },
          {
            from: 1864,
            to: 1871,
            text: "1.10.33",
            entity: "TOKEN",
          },
        ],
        [
          { from: 849, to: 857, text: "re-or-le", entity: "TOKEN" },
          { from: 847, to: 859, text: "more-or-less", entity: "TOKEN" },
        ],
        [
          { from: 1120, to: 1136, text: "for 'lorem ipsum", entity: "TOKEN" },
          { from: 1120, to: 1136, text: "for 'lorem ipsum", entity: "TOKEN" },
        ],
        [
          {
            from: 1872,
            to: 1911,
            text: 'of "de Finibus Bonorum et Malorum',
            entity: "TOKEN",
          },
          {
            from: 1872,
            to: 1911,
            text: 'of "de Finibus Bonorum et Malorum',
            entity: "TOKEN",
          },
        ],
        [
          { from: 1993, to: 1994, text: "a", entity: "TOKEN" },
          { from: 1993, to: 1994, text: "a", entity: "TOKEN" },
        ],
        [
          { from: 2132, to: 2136, text: "amet", entity: "TOKEN" },
          { from: 2132, to: 2136, text: "amet", entity: "TOKEN" },
        ],
        [
          { from: 2496, to: 2499, text: "m.", entity: "TOKEN" },
          { from: 2490, to: 2498, text: "Rackham.", entity: "TOKEN" },
        ],
      ])("%o %o", (actual: TestSelection, expected: TestSelection) => {
        const spanSelection = new SpanSelection();

        const textSelection = createTextSelection(actual);

        spanSelection.addSpan(textSelection);

        expect(spanSelection.spans[0]).toEqual(createSpan(expected));
        expect(spanSelection.spans).toHaveLength(1);
      });
    });

    describe("should allow selection by character level", () => {
      test.each([
        [
          { from: 4, to: 5, text: " ", entity: "TOKEN" },
          { from: 4, to: 5, text: " ", entity: "TOKEN" },
        ],
      ])("%o %o", (actual: TestSelection, expected: TestSelection) => {
        const spanSelection = new SpanSelection();
        spanSelection.config.allowCharacter = true;

        const textSelection = createTextSelection(actual);

        spanSelection.addSpan(textSelection);

        expect(spanSelection.spans[0]).toEqual(createSpan(expected));
      });
    });

    describe("should allow overlapping selection", () => {
      test.each([
        [
          [
            { from: 849, to: 857, text: "re-or-le", entity: "TOKEN" },
            { from: 849, to: 857, text: "re-or-le", entity: "TOKEN-2" },
          ],
          [
            {
              from: 847,
              to: 859,
              text: "more-or-less",
              entity: "TOKEN",
              level: 1,
            },
            {
              from: 847,
              to: 859,
              text: "more-or-less",
              entity: "TOKEN-2",
              level: 2,
            },
          ],
        ],
        [
          [
            {
              from: 65,
              to: 86,
              text: "ting and typese",
              entity: "TOKEN",
            },
            { from: 64, to: 69, text: "nting", entity: "TOKEN-2" },
          ],
          [
            {
              from: 61,
              to: 91,
              text: "printing and typesetting",
              entity: "TOKEN",
              level: 1,
            },
            { from: 61, to: 69, text: "printing", entity: "TOKEN-2", level: 2 },
          ],
        ],
        [
          [
            { from: 21, to: 32, text: "Lorem Ipsum", entity: "TOKEN" },
            { from: 21, to: 32, text: "Lorem Ipsum", entity: "TOKEN" },
            { from: 21, to: 32, text: "Lorem Ipsum", entity: "TOKEN" },
          ],
          [{ from: 21, to: 32, text: "Lorem Ipsum", entity: "TOKEN" }],
        ],
      ])("%o %o", (actual: TestSelection[], expected: TestSelection[]) => {
        const spanSelection = new SpanSelection();
        spanSelection.config.allowOverlap = true;

        actual.forEach((span) => {
          const textSelection = createTextSelection(span);

          spanSelection.addSpan(textSelection);
        });

        expect(spanSelection.spans).toEqual(expected.map((e) => createSpan(e)));
        expect(spanSelection.spans).toHaveLength(expected.length);
      });
    });

    describe("should allow overlapping selection for character level", () => {
      test.each([
        [
          [
            {
              from: 61,
              to: 91,
              text: "printing and typesetting",
              entity: "TOKEN",
            },
            { from: 61, to: 69, text: "printing", entity: "TOKEN-2" },
            { from: 69, to: 70, text: " ", entity: "TOKEN-3" },
          ],
          [
            {
              from: 61,
              to: 91,
              text: "printing and typesetting",
              entity: "TOKEN",
              level: 1,
            },
            { from: 61, to: 69, text: "printing", entity: "TOKEN-2", level: 2 },
            { from: 69, to: 70, text: " ", entity: "TOKEN-3", level: 2 },
          ],
        ],
      ])("%o %o", (actual: TestSelection[], expected: TestSelection[]) => {
        const spanSelection = new SpanSelection();
        spanSelection.config.allowOverlap = true;
        spanSelection.config.allowCharacter = true;

        actual.forEach((span) => {
          const textSelection = createTextSelection(span);

          spanSelection.addSpan(textSelection);
        });

        expect(spanSelection.spans).toEqual(expected.map((e) => createSpan(e)));
      });
    });

    describe("should replace current token when overlapping is not allowed", () => {
      test.each([
        [
          [
            {
              from: 61,
              to: 91,
              text: "printing and typesetting",
              entity: "TOKEN",
            },
            {
              from: 55,
              to: 97,
              text: "f the printing and typesetting indus",
              entity: "TOKEN",
            },
          ],
          {
            from: 54,
            to: 100,
            text: "of the printing and typesetting industry",
            entity: "TOKEN",
          },
        ],
      ])("%o %o", (actual: TestSelection[], expected: TestSelection) => {
        const spanSelection = new SpanSelection();

        actual.forEach((span) => {
          const textSelection = createTextSelection(span);

          spanSelection.addSpan(textSelection);
        });

        expect(spanSelection.spans[0]).toEqual(createSpan(expected));
        expect(spanSelection.spans).toHaveLength(1);
      });
    });

    describe("should not create span for one character when character level is not allowed", () => {
      test.each([{ from: 4, to: 5, text: " ", entity: "TOKEN" }])(
        "%o %o",
        (actual: TestSelection) => {
          const spanSelection = new SpanSelection();
          spanSelection.config.allowCharacter = false;

          const textSelection = createTextSelection(actual);
          spanSelection.addSpan(textSelection);

          expect(spanSelection.spans).toEqual([]);
        }
      );
    });

    describe("should remove span created", () => {
      test("should remove span", () => {
        const spanSelection = new SpanSelection();
        const textSelection = createTextSelection({
          from: 10,
          to: 17,
          text: "rem Ips",
          entity: "TOKEN",
        });

        const expectedSpan = createSpan({
          from: 8,
          to: 19,
          text: "Lorem Ipsum",
          entity: "TOKEN",
        });

        spanSelection.addSpan(textSelection);

        expect(spanSelection.spans).toEqual([expectedSpan]);

        spanSelection.removeSpan(expectedSpan);

        expect(spanSelection.spans).toHaveLength(0);
      });

      test("should remove span and re calculate the overlapping", () => {
        const spanSelection = new SpanSelection();
        spanSelection.config.allowOverlap = true;

        const textSelection1 = createTextSelection({
          from: 10,
          to: 17,
          text: "rem Ips",
          entity: "TOKEN",
        });

        const textSelection2 = createTextSelection({
          from: 8,
          to: 19,
          text: "Lorem Ipsum",
          entity: "TOKEN-2",
        });

        spanSelection.addSpan(textSelection1);
        spanSelection.addSpan(textSelection2);

        expect(spanSelection.spans[0].overlap.level).toBe(1);
        expect(spanSelection.spans[1].overlap.level).toBe(2);

        spanSelection.removeSpan(spanSelection.spans[0]);

        expect(spanSelection.spans).toHaveLength(1);
        expect(spanSelection.spans[0].from).toBe(textSelection2.from);
        expect(spanSelection.spans[0].to).toBe(textSelection2.to);
        expect(spanSelection.spans[0].overlap.level).toBe(1);
      });
    });

    describe("should replace the entity for the span", () => {
      test("should replace entity", () => {
        const spanSelection = new SpanSelection();
        const textSelection = createTextSelection({
          from: 10,
          to: 17,
          text: "rem Ips",
          entity: "TOKEN",
        });

        const expectedSpan = createSpan({
          from: 8,
          to: 19,
          text: "Lorem Ipsum",
          entity: "TOKEN",
        });

        const newEntity = {
          id: "TOKEN-2",
          text: "TOKEN-2",
          value: "TOKEN-2",
        };

        spanSelection.addSpan(textSelection);

        expect(spanSelection.spans).toEqual([expectedSpan]);

        spanSelection.replaceEntity(expectedSpan, newEntity);

        expect(spanSelection.spans[0].entity).toEqual(newEntity);
      });

      test("should not replace entity if span is not found", () => {
        const spanSelection = new SpanSelection();
        const textSelection = createTextSelection({
          from: 10,
          to: 17,
          text: "rem Ips",
          entity: "TOKEN",
        });
        const expectedSpan = createSpan({
          from: 8,
          to: 19,
          text: "Lorem Ipsum",
          entity: "TOKEN",
        });

        const noExisting = createSpan({
          from: 300,
          to: 21,
          text: "xxx",
          entity: "TOKEN-3",
        });

        spanSelection.addSpan(textSelection);

        expect(spanSelection.spans).toEqual([expectedSpan]);

        spanSelection.replaceEntity(noExisting, {
          id: "TOKEN-2",
        });

        expect(spanSelection.spans[0].entity.id).toEqual("TOKEN");
      });
    });

    describe("should not create span for selections", () => {
      test("should not create out of range span", () => {
        const spanSelection = new SpanSelection();
        const textSelection1 = createTextSelection({
          from: -1,
          to: 10,
          text: "NOT EXIST",
          entity: "TOKEN",
        });

        spanSelection.addSpan(textSelection1);

        expect(spanSelection.spans).toEqual([]);
      });
    });

    describe("Unexpected issues", () => {
      test("should select whole word", () => {
        const node = {
          textContent: ISSUES.NOT_SELECTING_WHOLE_WORD,
        } as HTMLElement;

        const spanSelection = new SpanSelection();
        const textSelection = createTextSelection(
          {
            from: 0,
            to: 5,
            text: "Apple",
            entity: "TOKEN",
          },
          node
        );

        const expectedSpan = createSpan(
          {
            from: 0,
            to: 14,
            text: ISSUES.NOT_SELECTING_WHOLE_WORD,
            entity: "TOKEN",
          },
          node
        );

        spanSelection.addSpan(textSelection);

        expect(spanSelection.spans[0]).toEqual(expectedSpan);
      });
    });
  });

  describe("loadSpans", () => {
    test.each([
      [
        { from: -1, to: 5, text: "What ", entity: "TOKEN" },
        { from: 0, to: 5, text: "What ", entity: "TOKEN" },
      ],
      [
        { from: 2496, to: 2499, text: "m.", entity: "TOKEN" },
        { from: 2496, to: 2498, text: "m.", entity: "TOKEN" },
      ],
    ])("%o %o", (actual: TestSelection, expected: TestSelection) => {
      const spanSelection = new SpanSelection();

      const span = createSpan(actual);

      spanSelection.loadSpans([span]);

      expect(spanSelection.spans[0]).toEqual(createSpan(expected));
      expect(spanSelection.spans).toHaveLength(1);
    });
  });
});
