interface Field {
  id: string;
  name: string;
  required: boolean;
  title: string;
  settings: any;
}

export interface IFieldRepository {
  getFields(datasetId: string): Promise<Field[]>;
}
