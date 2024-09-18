interface Question {
  id: string;
  description?: string;
  name: string;
  title: string;
  required: boolean;
  settings: unknown;
}

export interface IQuestionRepository {
  getQuestions(datasetId: string): Promise<Question[]>;
}
