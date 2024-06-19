import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Response, BackendQuestion } from "../types";
import { mediumCache, revalidateCache } from "./AxiosCache";
import { Question } from "~/v1/domain/entities/question/Question";
import { IQuestionRepository } from "~/v1/domain/services/IQuestionRepository";

export const enum QUESTION_API_ERRORS {
  GET_QUESTIONS = "ERROR_FETCHING_QUESTIONS",
  UPDATE = "ERROR_PATCHING_QUESTIONS",
}

export class QuestionRepository implements IQuestionRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getQuestions(datasetId: string): Promise<BackendQuestion[]> {
    try {
      const { data } = await this.axios.get<Response<BackendQuestion[]>>(
        `/v1/datasets/${datasetId}/questions`,
        mediumCache()
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

      revalidateCache(`/v1/datasets/${question.datasetId}/questions`);

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
    const newDescription =
      description?.trim() !== "" ? description.trim() : null;

    return {
      title,
      description: newDescription,
      settings,
    };
  }
}
