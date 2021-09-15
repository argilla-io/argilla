import { ObservationDataset } from "./Dataset";
import { BaseRecord, BaseSearchQuery, BaseSearchResults } from "./Common";

class Text2TextRecord extends BaseRecord {
  text;

  constructor({ text, ...superData }) {
    super(superData);
    this.text = text;
  }
  recordTitle() {
    return this.text;
  }
}

class Text2TextSearchQuery extends BaseSearchQuery {
  score;

  constructor(data) {
    const { score, ...superData } = data;
    super(superData);

    this.score = score;
  }
}

class Text2TextSearchResults extends BaseSearchResults {
  constructor({ total, records, aggregations }) {
    super({
      total,
      aggregations,
      records: (records || []).map((record) => new Text2TextRecord(record)),
    });
  }
}

class Text2TextDataset extends ObservationDataset {
  static entity = "text2_text";

  static fields() {
    return {
      ...super.fields(),
      query: this.attr({}, (data) => {
        return new Text2TextSearchQuery(data);
      }),
      sort: this.attr([]),
      results: this.attr({}, (data) => new Text2TextSearchResults(data)),
      globalResults: this.attr({}),
    };
  }
}

export {
  Text2TextDataset,
  Text2TextRecord,
  Text2TextSearchResults,
  Text2TextSearchQuery,
};
