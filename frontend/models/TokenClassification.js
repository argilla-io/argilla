import { ObservationDataset, USER_DATA_METADATA_KEY } from "./Dataset";
import { BaseRecord, BaseSearchQuery, BaseSearchResults } from "./Common";

class TokenClassificationRecord extends BaseRecord {
  tokens;
  raw_text;

  visualTokens;

  constructor({ tokens, raw_text, ...superData }) {
    super({ ...superData });
    const { visualTokens } = tokens.reduce(
      ({ visualTokens, startPosition }, token) => {
        const start = raw_text.indexOf(token, startPosition);
        const end = start + token.length;
        return {
          visualTokens: [...visualTokens, { start, end, text: token }],
          startPosition: end,
        };
      },
      {
        visualTokens: [],
        startPosition: 0,
      }
    );
    this.tokens = tokens;
    this.raw_text = raw_text;
    this.visualTokens = visualTokens;
  }
}

class TokenClassificationSearchQuery extends BaseSearchQuery {
  query_text;

  constructor({ query_text, ...superData }) {
    super(superData);
    this.query_text = query_text;
  }
}

class TokenClassificationSearchResults extends BaseSearchResults {
  constructor({ total, records, aggregations }) {
    super({
      total,
      aggregations,
      records: (records || []).map(
        (record) => new TokenClassificationRecord(record)
      ),
    });
  }
}

class TokenClassificationDataset extends ObservationDataset {
  static entity = "token_classification";

  static fields() {
    return {
      ...super.fields(),
      query: this.attr({}, (data) => {
        return new TokenClassificationSearchQuery(data);
      }),
      sort: this.attr([]),
      results: this.attr(
        {},
        (data) => new TokenClassificationSearchResults(data)
      ),
      globalResults: this.attr({}),
    };
  }

  get entities() {
    const { entities } = (this.metadata || {})[USER_DATA_METADATA_KEY] || {};

    const usedChars = [];
    const characters = "1234567890".split("");
    const aggregations = this.globalResults.aggregations;
    const names = [
      ...new Set(
        (entities || [])
          .filter((e) => e && e.trim())
          .concat(Object.keys(aggregations.annotated_as))
          .concat(Object.keys(aggregations.predicted_as))
      ),
    ];
    names.sort();
    return names.map((name) => {
      let shortcut = name.slice(0, 1).toUpperCase();
      const availableChars = characters.filter((c) => !usedChars.includes(c));
      if (availableChars.indexOf(shortcut) === -1) {
        [shortcut] = availableChars;
      }
      function colorId(name) {
        const firstLetter = name.slice(0, 1);
        const lastLetter = name.slice(-1);
        const asciiCode = firstLetter.charCodeAt(0) + lastLetter.charCodeAt(0);
        const nameLength =
          name.length < 30 ? name.length : Math.round(name.length / 3);
        const random = Math.round((asciiCode - nameLength) / 10) + nameLength;
        return random;
      }
      usedChars.push(shortcut);
      return {
        colorId: colorId(name),
        text: name,
        shortCut: shortcut,
      };
    });
  }
}

export {
  TokenClassificationDataset,
  TokenClassificationRecord,
  TokenClassificationSearchResults,
  TokenClassificationSearchQuery,
};
