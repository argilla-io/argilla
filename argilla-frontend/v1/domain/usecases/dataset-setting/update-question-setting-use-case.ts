import { Question } from "../../entities/question/Question";
import { QuestionRepository } from "~/v1/infrastructure/repositories";

export class UpdateQuestionSettingUseCase {
  constructor(private readonly questionRepository: QuestionRepository) {}

  async execute(question: Question) {
    if (!question.isQuestionValid) {
      throw new Error("Question is not valid for update");
    }

    await this.questionRepository.update(question);

    question.update();
  }
}
