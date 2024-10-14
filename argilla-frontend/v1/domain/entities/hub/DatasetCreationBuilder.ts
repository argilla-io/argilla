import { DatasetCreation } from "./DatasetCreation";
import { Subset } from "./Subset";

export interface Feature {
  dtype: "string" | "int32" | "int64";
  _type: "Value" | "Image" | "ClassLabel";
  names?: string[];
}

export class DatasetCreationBuilder {
  private readonly subsets: Subset[] = [];
  private readonly datasetName: string;
  constructor(private readonly repoId: string, datasetInfo: any) {
    if (datasetInfo.default) {
      this.datasetName = datasetInfo.default.dataset_name;

      for (const [name, value] of Object.entries<Feature>(datasetInfo)) {
        this.subsets.push(new Subset(name, value));
      }
    } else {
      const firstKey = Object.keys(datasetInfo)[0];
      const dataset = datasetInfo[firstKey];

      this.datasetName = dataset.dataset_name;
      this.subsets.push(new Subset(firstKey, dataset));
    }
  }

  build(): DatasetCreation {
    return new DatasetCreation(this.repoId, this.datasetName, this.subsets);
  }
}
