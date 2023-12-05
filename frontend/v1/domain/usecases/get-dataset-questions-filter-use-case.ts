import { Question } from "../entities/question/Question";
import { QuestionRepository } from "~/v1/infrastructure/repositories";

export class GetDatasetQuestionsFilterUseCase {
  constructor(private readonly questionRepository: QuestionRepository) {}

  async execute(datasetId: string): Promise<Question[]> {
    const backendQuestions = await this.questionRepository.getQuestions(
      datasetId
    );

    const questions = backendQuestions.map((question) => {
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

    return questions.filter(this.visibleTypeOfQuestions);
  }

  private visibleTypeOfQuestions(question: Question): boolean {
    return (
      question.isMultiLabelType ||
      question.isSingleLabelType ||
      question.isRatingType
    );
  }
}
