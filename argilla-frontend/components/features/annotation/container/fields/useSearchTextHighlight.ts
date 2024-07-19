declare class Highlight {
  constructor(...ranges: Range[]);
}

declare namespace CSS {
  const highlights: {
    set(className: string, highlight: Highlight): void;
    delete(className: string): void;
    clear(): void;
  };
}

const DSLChars = ["|", "+", "-", "*"];

export const useSearchTextHighlight = (fieldId: string) => {
  const FIELD_ID_TO_HIGHLIGHT = `fields-content-${fieldId}`;
  const HIGHLIGHT_CLASS = `search-text-highlight-${fieldId}`;

  const scapeDSLChars = (value: string) => {
    let output = value;

    for (const char of DSLChars) {
      output = output.replaceAll(char, " ");
    }

    return output
      .split(" ")
      .map((w) => w.trim())
      .filter(Boolean);
  };

  const createRangesToHighlight = (
    fieldComponent: HTMLElement,
    searchText: string
  ) => {
    CSS.highlights.delete(HIGHLIGHT_CLASS);

    const ranges = [];

    const getTextNodesUnder = (el) => {
      const textNodes = [];
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);

      while (walker.nextNode()) {
        textNodes.push(walker.currentNode);
      }

      return textNodes.filter((node) => node.nodeValue.trim().length > 0);
    };

    const getAllCoincidences = (textNode, word, mode: "PARTIAL" | "WORD") => {
      const indexes = [];

      if (mode === "PARTIAL") {
        let startIndex = 0;

        let index;

        while (
          (index = textNode.nodeValue
            .toLowerCase()
            .indexOf(word.toLowerCase(), startIndex)) > -1
        ) {
          const newCoincidence = {
            start: index,
            end: index + word.length,
          };

          indexes.push(newCoincidence);

          startIndex = newCoincidence.end;
        }
      }

      if (mode === "WORD") {
        const regex = new RegExp(`\\b${word}\\b`, "gi");

        let result;

        while ((result = regex.exec(textNode.nodeValue.toLowerCase()))) {
          indexes.push({
            start: result.index,
            end: result.index + result[0].length,
          });
        }
      }

      return indexes;
    };

    const createRanges = (textNode, indexes) => {
      const ranges = [];

      for (const index of indexes) {
        const range = new Range();

        range.setStart(textNode, index.start);
        range.setEnd(textNode, index.end);

        ranges.push(range);
      }

      return ranges;
    };

    const textNodes = getTextNodesUnder(fieldComponent);
    const words = scapeDSLChars(searchText);

    for (const textNode of textNodes) {
      for (const word of words) {
        const indexes = getAllCoincidences(textNode, word, "WORD");

        const newRanges = createRanges(textNode, indexes);

        ranges.push(...newRanges);
      }
    }

    return ranges;
  };

  const highlightText = (searchText: string) => {
    const fieldComponent = document.getElementById(FIELD_ID_TO_HIGHLIGHT);
    if (!searchText || !fieldComponent) return;

    const ranges = createRangesToHighlight(fieldComponent, searchText);

    CSS.highlights.set(HIGHLIGHT_CLASS, new Highlight(...ranges));
  };

  return {
    highlightText,
  };
};
