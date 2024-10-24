import { DatasetCreation } from "./DatasetCreation";
import { Subset } from "./Subset";

export interface Feature {
  dtype: "string" | "int32" | "int64";
  _type: "Value" | "Image" | "ClassLabel";
  names?: string[];
  feature?: Feature;
}

export class DatasetCreationBuilder {
  private readonly subsets: Subset[] = [];
  private readonly datasetName: string;
  constructor(private readonly repoId: string, datasetInfo: any) {
    const firstKey = Object.keys(datasetInfo)[0];
    const defaultSubset = datasetInfo[firstKey];

    this.datasetName = defaultSubset.dataset_name;

    for (const [name, value] of Object.entries<Feature>(datasetInfo)) {
      this.subsets.push(new Subset(name, value));
    }
  }

  build(): DatasetCreation {
    return new DatasetCreation(this.repoId, this.datasetName, this.subsets);
  }
}
