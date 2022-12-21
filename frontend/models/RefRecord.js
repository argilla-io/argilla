import { Model } from "@vuex-orm/core";

import { TokenClassificationRecord } from "@/models/TokenClassification";
import { TextClassificationRecord } from "@/models/TextClassification";
import { Text2TextRecord } from "@/models/Text2Text";

function getFactoryRecordTaskType(task) {
  let recordClass = null;
  switch (task) {
    case "TextClassification":
      recordClass = TextClassificationRecord;
      break;
    case "TokenClassification":
      recordClass = TokenClassificationRecord;
      break;
    case "Text2Text":
      recordClass = Text2TextRecord;
      break;
    default:
      throw Error("unknown dataset task");
  }
  return recordClass;
}

class RefRecord extends Model {
  static entity = "refRecords";
  static primaryKey = ["record_id", "dataset_id"];

  static fields() {
    return {
      id: this.uid(),
      dataset_id: this.attr(""),
      task: this.attr(""),
      record_id: this.attr(""),
      record_data: this.attr(null),
    };
  }

  get record_object() {
    const RecordClass = getFactoryRecordTaskType(this.task);
    const referenceRecord = new RecordClass(this.record_data);
    return referenceRecord;
  }
}

export { RefRecord };
