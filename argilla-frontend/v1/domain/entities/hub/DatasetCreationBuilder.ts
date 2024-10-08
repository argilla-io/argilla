import { DatasetCreation } from "./DatasetCreation";
import { Subset } from "./Subset";

export interface Feature {
  dtype: "string" | "int32" | "int64";
  _type: "Value" | "Image" | "ClassLabel";
  names?: string[];
}

export class DatasetCreationBuilder {
  private readonly subsets: Subset[] = [];
  constructor(datasetInfo: any) {
    debugger;
    if (datasetInfo.default) {
      for (const [name, value] of Object.entries<Feature>(datasetInfo)) {
        this.subsets.push(new Subset(name, value));
      }
    } else {
      this.subsets.push(new Subset("default", datasetInfo));
    }
  }

  build(): DatasetCreation {
    return new DatasetCreation(this.subsets);
  }
}
