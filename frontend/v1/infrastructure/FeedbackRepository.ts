import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Field } from "../domain/entities/Field";
import { Question } from "../domain/entities/Question";

const TYPE_OF_FEEDBACK = {
  ERROR_FETCHING_QUESTIONS: "ERROR_FETCHING_QUESTIONS",
  ERROR_FETCHING_FIELDS: "ERROR_FETCHING_FIELDS",
};

interface Response<T> {
  items: T;
}

interface RatingSetting {
  type: "rating";
  options: {
    value: number;
  }[];
}

interface TextSetting {
  type: "text";
  use_markdown: boolean;
}

interface RankingSetting {
  type: "ranking";
  options: {
    description?: string;
    text: string;
    value: string;
  }[];
}

interface MultiSelectionSetting {
  type: "multi_label_selection";
  visible_options: number;
  options: {
    description?: string;
    text: string;
    value: string;
  }[];
}

interface SingleSelectionSetting {
  type: "label_selection";
  options: {
    description?: string;
    text: string;
    value: string;
  }[];
}

interface BackendQuestion {
  id: string;
  description?: string;
  name: string;
  title: string;
  required: boolean;
  settings:
    | TextSetting
    | MultiSelectionSetting
    | SingleSelectionSetting
    | RatingSetting
    | RankingSetting;
}

interface BackendField {
  id: string;
  name: string;
  required: boolean;
  title: string;
  settings:
    | TextSetting
    | MultiSelectionSetting
    | SingleSelectionSetting
    | RatingSetting
    | RankingSetting;
}

export class FeedbackRepository {
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
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_QUESTIONS,
      };
    }
  }

  async getFields(datasetId: string): Promise<Field[]> {
    try {
      const { data } = await this.axios.get<Response<BackendField[]>>(
        `/v1/datasets/${datasetId}/fields`
      );

      return data.items.map((field) => {
        return new Field(
          field.id,
          field.name,
          field.title,
          datasetId,
          field.required,
          field.settings
        );
      });
    } catch (err) {
      throw {
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_FIELDS,
      };
    }
  }
}
