class BaseRecord {
  id;
  metadata;
  prediction;
  annotation;
  predicted;
  status;

  selected;

  constructor({
    id,
    metadata,
    prediction,
    annotation,
    predicted,
    status,
    selected,
  }) {
    this.id = id;
    this.metadata = metadata;
    this.prediction = prediction;
    this.annotation = annotation;
    this.predicted = predicted;
    this.status = status;
    this.selected = selected || false;
  }
}

class BaseSearchQuery {
  multi_label;
  predicted_as;
  annotated_as;
  annotated_by;
  predicted_by;
  status;
  predicted;
  metadata;
  text;
  from;
  limit;

  constructor({
    predicted_as,
    annotated_as,
    annotated_by,
    predicted_by,
    status,
    predicted,
    metadata,
    text,
  }) {
    this.predicted_as = predicted_as;
    this.annotated_as = annotated_as;
    this.annotated_by = annotated_by;
    this.predicted_by = predicted_by;
    this.status = status;
    this.predicted = predicted;
    this.metadata = metadata;
    this.text = text;
  }
}

class BaseSearchResults {
  total;
  records;
  aggregations;

  constructor({ total, records, aggregations }) {
    this.total = total || 0;
    this.records = records;
    this.aggregations = aggregations || {};
  }
}

export { BaseRecord, BaseSearchQuery, BaseSearchResults };
