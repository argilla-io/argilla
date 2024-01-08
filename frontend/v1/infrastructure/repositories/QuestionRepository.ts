import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Response, BackendQuestion } from "../types";
import { Question } from "~/v1/domain/entities/question/Question";

export const enum QUESTION_API_ERRORS {
  GET_QUESTIONS = "ERROR_FETCHING_QUESTIONS",
  UPDATE = "ERROR_PATCHING_QUESTIONS",
}

export class QuestionRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getQuestions(datasetId: string): Promise<BackendQuestion[]> {
    try {
      const { data } = await this.axios.get<Response<BackendQuestion[]>>(
        `/v1/datasets/${datasetId}/questions`,
        { headers: { "cache-control": "max-age=120" } }
      );

      return data.items;
    } catch (err) {
      throw {
        response: QUESTION_API_ERRORS.GET_QUESTIONS,
      };
    }
  }

  async update(question: Question): Promise<BackendQuestion> {
    try {
      const { data } = await this.axios.patch<BackendQuestion>(
        `/v1/questions/${question.id}`,
        this.createRequest(question)
      );

      return data;
    } catch (err) {
      throw {
        response: QUESTION_API_ERRORS.UPDATE,
      };
    }
  }

  private createRequest({
    description,
    title,
    settings,
  }: Question): Partial<BackendQuestion> {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { options, ...rest } = settings;

    const newDescription =
      description?.trim() !== "" ? description.trim() : null;

    return {
      title,
      description: newDescription,
      settings: {
        ...rest,
      },
    };
  }
}
