let classInstance;
let globalState = {
  record: null,
  vector: null,
};

class ReferenceRecordStateUtility {
  constructor(record, vector) {
    if (classInstance) {
      throw new Error("New instance cannot be created!!");
    }

    classInstance = this;

    globalState.record = record;
    globalState.vector = vector;
  }

  referenceRecord() {
    return globalState.record;
  }

  setReferenceRecord(record) {
    globalState.record = record;
  }

  referenceVector() {
    return globalState.vector;
  }

  setReferenceVector(vector) {
    globalState.vector = vector;
  }

  cleanInstance() {
    globalState.record = null;
    globalState.vector = null;
  }
}

let ReferenceRecord = Object.freeze(new ReferenceRecordStateUtility());

export { ReferenceRecord };
