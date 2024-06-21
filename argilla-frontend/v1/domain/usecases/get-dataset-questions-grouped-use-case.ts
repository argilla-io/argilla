import { Question } from "../entities/question/Question";
import { IQuestionRepository } from "../services/IQuestionRepository";

export class GetDatasetQuestionsGroupedUseCase {
  constructor(private readonly questionRepository: IQuestionRepository) {}

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

    return this.groupQuestionsByType(questions);
  }

  private groupQuestionsByType(questions: Question[]): Question[] {
    const groupedQuestions: Question[] = [];
    for (const question of questions) {
      if (groupedQuestions.some((q) => q.type.value === question.type.value))
        continue;

      groupedQuestions.push(question);
    }

    return groupedQuestions;
  }
}
