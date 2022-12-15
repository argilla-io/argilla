class ReferenceRecord {
  #record = null;
  #vector = null;

  constructor(record, vector) {
    this.#record = record;
    this.#vector = vector;
  }

  get referenceRecord() {
    return this.#record;
  }

  set setReferenceRecord(record) {
    this.#record = record;
  }

  get referenceVector() {
    return this.#vector;
  }

  set setReferenceVector(vector) {
    this.#vector = vector;
  }
}

export { ReferenceRecord };
