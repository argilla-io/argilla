import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Response, BackendQuestion } from "../types";
import { Question } from "~/v1/domain/entities/question/Question";

export class QuestionRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getQuestions(datasetId: string): Promise<Question[]> {
    try {
      const { data } = await this.axios.get<Response<BackendQuestion[]>>(
        `/v1/datasets/${datasetId}/questions`
      );

      return data.items.map((question) => {
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
    } catch (err) {
      throw {
        response: "ERROR_FETCHING_QUESTIONS",
      };
    }
  }
}
