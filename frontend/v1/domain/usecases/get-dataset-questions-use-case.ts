import { Question } from "../entities/question/Question";
import { QuestionRepository } from "~/v1/infrastructure/repositories";

export class GetDatasetQuestionsUseCase {
  constructor(private readonly questionRepository: QuestionRepository) {}

  async execute(datasetId: string): Promise<Question[]> {
    const backendQuestions = await this.questionRepository.getQuestions(
      datasetId
    );

    return backendQuestions.map((question) => {
      return new Question(
        question.id,
        question.name,
        question.description,
        datasetId,
        question.title,
        question.required,
        question.settings
      );
    });
  }
}
