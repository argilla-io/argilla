import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import {
  CORRESPONDING_FIELD_COMPONENT_TYPE_FROM_API,
  CORRESPONDING_QUESTION_COMPONENT_TYPE_FROM_API,
} from "~/components/feedback-task/feedbackTask.properties";

const TYPE_OF_FEEDBACK = {
  ERROR_FETCHING_QUESTIONS: "ERROR_FETCHING_QUESTIONS",
  ERROR_FETCHING_FIELDS: "ERROR_FETCHING_FIELDS",
};

export class FeedbackRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getQuestions(datasetId: string): Promise<unknown[]> {
    try {
      const { data } = await this.axios.get(
        `/v1/datasets/${datasetId}/questions`
      );

      return this.factoryQuestionsForOrm(data.items, datasetId);
    } catch (err) {
      throw {
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_QUESTIONS,
      };
    }
  }

  async getFields(datasetId: string): Promise<unknown[]> {
    try {
      const { data } = await this.axios.get(`/v1/datasets/${datasetId}/fields`);

      return this.factoryFieldsForOrm(data.items, datasetId);
    } catch (err) {
      throw {
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_FIELDS,
      };
    }
  }

  private factoryQuestionsForOrm(
    initialQuestions: unknown[],
    datasetId: string
  ): unknown[] {
    return initialQuestions.map(
      (
        {
          id: questionId,
          name: questionName,
          title: questionTitle,
          required: isRequired,
          settings: questionSettings,
          description: questionDescription,
        },
        index
      ) => {
        const componentTypeFromBack = questionSettings.type.toLowerCase();
        const componentType =
          CORRESPONDING_QUESTION_COMPONENT_TYPE_FROM_API[componentTypeFromBack];

        const formattedOptions = this.formatOptionsFromQuestionApi(
          questionSettings.options,
          questionName
        );

        return {
          id: questionId,
          name: questionName,
          dataset_id: datasetId,
          order: index,
          question: questionTitle,
          options: formattedOptions,
          is_required: isRequired,
          component_type: componentType,
          placeholder: questionSettings?.placeholder ?? null,
          description: questionDescription ?? null,
          settings: questionSettings,
        };
      }
    );
  }

  private formatOptionsFromQuestionApi(options, questionName) {
    if (options) {
      return options?.map((option) => {
        const optionText = option.text ?? option.value;
        const paramObject = {
          value: option.value,
          text: optionText,
          prefixId: questionName,
          suffixId: option.value,
        };

        return this.factoryOption(paramObject);
      });
    }

    return [
      this.factoryOption({
        value: "",
        prefixId: questionName,
      }),
    ];
  }

  private factoryOption({ value = null, text = "", prefixId, suffixId }: any) {
    return {
      id: `${prefixId}${suffixId ? `_${suffixId}` : ""}`,
      value,
      text,
    };
  }

  private factoryFieldsForOrm(initialFields: unknown[], datasetId: string) {
    return initialFields.map(
      (
        {
          id: fieldId,
          name: fieldName,
          title: fieldTitle,
          required: isRequired,
          settings: fieldSettings,
        },
        index
      ) => {
        const componentTypeFromBack =
          fieldSettings?.type?.toLowerCase() ?? null;

        const componentType = componentTypeFromBack
          ? CORRESPONDING_FIELD_COMPONENT_TYPE_FROM_API[componentTypeFromBack]
          : null;

        return {
          id: fieldId,
          name: fieldName,
          dataset_id: datasetId,
          order: index,
          title: fieldTitle,
          is_required: isRequired,
          component_type: componentType,
          settings: fieldSettings,
        };
      }
    );
  }
}
