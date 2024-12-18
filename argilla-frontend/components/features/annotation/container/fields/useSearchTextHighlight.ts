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

type Indexes = { start: number; end: number }[];
type Coincidences = {
  textNode: Node;
  indexes: Indexes;
}[];

const DSLChars = ["|", "+", "-", "*"];
const isCSSHighlightsSupported = !!CSS.highlights;

export const useSearchTextHighlight = (fieldId: string) => {
  const FIELD_ID_TO_HIGHLIGHT = `fields-content-${fieldId}`;
  const HIGHLIGHT_CLASS = `search-text-highlight-${fieldId}`;

  const createIndexesToHighlight = (
    fieldComponent: HTMLElement,
    searchText: string
  ): Coincidences => {
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

    const getTextNodesUnder = (el) => {
      const textNodes: Node[] = [];
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);

      while (walker.nextNode()) {
        textNodes.push(walker.currentNode);
      }

      return textNodes.filter((node) => node.nodeValue.trim().length > 0);
    };

    const getAllCoincidences = (
      textNode: Node,
      word: string,
      mode: "PARTIAL" | "WORD"
    ) => {
      const indexes: Indexes = [];

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

    const textNodes = getTextNodesUnder(fieldComponent);
    const words = scapeDSLChars(searchText);

    const coincidences = [];

    for (const textNode of textNodes) {
      const indexes = [];
      for (const word of words) {
        const index = getAllCoincidences(textNode, word, "WORD");

        indexes.push(...index);
      }

      coincidences.push({
        textNode,
        indexes,
      });
    }

    return coincidences;
  };

  const highlightCoincidences = (coincidences: Coincidences) => {
    if (isCSSHighlightsSupported) {
      const createRanges = (coincidences: Coincidences) => {
        const ranges = [];

        for (const coincidence of coincidences) {
          for (const index of coincidence.indexes) {
            const range = new Range();

            range.setStart(coincidence.textNode, index.start);
            range.setEnd(coincidence.textNode, index.end);

            ranges.push(range);
          }
        }

        return ranges;
      };

      const ranges = createRanges(coincidences);

      return CSS.highlights.set(HIGHLIGHT_CLASS, new Highlight(...ranges));
    }

    for (const coincidence of coincidences) {
      let highlightedHTML = "";
      let offset = 0;
      const textContent = coincidence.textNode.nodeValue;

      coincidence.indexes
        .sort((a, b) => a.start - b.start)
        .forEach(({ start, end }) => {
          highlightedHTML += textContent.slice(offset, start);

          highlightedHTML += `<span class=${HIGHLIGHT_CLASS}>${textContent.slice(
            start,
            end
          )}</span>`;

          offset = end;
        });

      highlightedHTML += textContent.slice(offset);

      if (coincidence.textNode.parentElement)
        coincidence.textNode.parentElement.innerHTML = highlightedHTML;
    }
  };

  const highlightText = (searchText: string) => {
    const fieldComponent = document.getElementById(FIELD_ID_TO_HIGHLIGHT);

    if (isCSSHighlightsSupported) CSS.highlights.delete(HIGHLIGHT_CLASS);
    else {
      const currentSpans = document.getElementsByClassName(HIGHLIGHT_CLASS);

      for (const span of Array.from(currentSpans)) {
        const parent = span.parentElement;
        if (!parent) continue;

        parent.innerHTML = parent.innerHTML.replaceAll(
          span.outerHTML,
          span.innerHTML
        );
      }
    }

    if (!searchText || !fieldComponent) {
      return;
    }

    const coincidences = createIndexesToHighlight(fieldComponent, searchText);

    highlightCoincidences(coincidences);
  };

  return {
    highlightText,
  };
};
