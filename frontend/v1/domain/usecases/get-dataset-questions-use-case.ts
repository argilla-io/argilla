import { Question } from "../entities/question/Question";
import { QuestionRepository } from "~/v1/infrastructure/repositories";

export class GetDatasetQuestionsUseCase {
  constructor(private readonly questionRepository: QuestionRepository) {}

  execute(datasetId: string): Promise<Question[]> {
    return this.questionRepository.getQuestions(datasetId);
  }
}
