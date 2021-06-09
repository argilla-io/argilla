import { ObservationDataset, USER_DATA_METADATA_KEY } from "./Dataset";
import { BaseRecord, BaseSearchQuery, BaseSearchResults } from "./Common";

class TextClassificationRecord extends BaseRecord {
  inputs;

  constructor({ inputs, explanation, multi_label, ...superData }) {
    super(superData);
    this.inputs = inputs;
    this.explanation = explanation;
    this.multi_label = multi_label;
  }
}

class TextClassificationSearchQuery extends BaseSearchQuery {
  confidence;

  constructor(data) {
    const { confidence, ...superData } = data;
    super(superData);

    this.confidence = confidence;
  }
}

class TextClassificationSearchResults extends BaseSearchResults {
  constructor({ total, records, aggregations }) {
    super({
      total,
      aggregations,
      records: (records || []).map(
        (record) => new TextClassificationRecord(record)
      ),
    });
  }
}

class TextClassificationDataset extends ObservationDataset {
  static entity = "text_classification";

  static fields() {
    return {
      ...super.fields(),
      query: this.attr({}, (data) => {
        return new TextClassificationSearchQuery(data);
      }),
      sort: this.attr([]),
      results: this.attr(
        {},
        (data) => new TextClassificationSearchResults(data)
      ),
      globalResults: this.attr({}),
    };
  }

  get labels() {
    const { labels } = (this.metadata || {})[USER_DATA_METADATA_KEY] || {};
    const aggregations = this.globalResults.aggregations;

    const uniqueLabels = [
      ...new Set(
        (labels || [])
          .filter((l) => l && l.trim())
          .concat(Object.keys(aggregations.annotated_as))
          .concat(Object.keys(aggregations.predicted_as))
      ),
    ];
    uniqueLabels.sort();
    return uniqueLabels;
  }
}

export {
  TextClassificationDataset,
  TextClassificationRecord,
  TextClassificationSearchResults,
  TextClassificationSearchQuery,
};
