import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { useResolve } from "ts-injecty";
import { Feedback } from "~/v1/domain/entities/Feedback";
import { useFeedback } from "~/v1/infrastructure/FeedbackStorage";

export const useFeedbackTask = () => {
  const feedbackStore = useFeedback();
  const repository = useResolve(FeedbackRepository);
  const fetch = async (datasetId: string) => {
    // FETCH questions AND fields by dataset
    const { items: questions } = await repository.getQuestions(datasetId);
    const { items: fields } = await repository.getFields(datasetId);
    console.log("question", questions);
    console.log("fields", fields);
    return new Feedback();
    // FORMAT questions AND fields to have the shape of ORM
    // const formattedQuestionsForOrm = this.factoryQuestionsForOrm(questions);
    // const formattedFieldsForOrm = this.factoryFieldsForOrm(fields);
    // UPSERT formatted questions in ORM
    // await upsertDatasetQuestions(formattedQuestionsForOrm);
    // await upsertDatasetFields(formattedFieldsForOrm);
  };
  const loadFeedback = async (datasetId: string) => {
    const response = await fetch(datasetId);
  };
  return { feedback: feedbackStore.state, loadFeedback };
};
const TYPE_OF_FEEDBACK = {
  ERROR_FETCHING_QUESTIONS: "ERROR_FETCHING_QUESTIONS",
  ERROR_FETCHING_FIELDS: "ERROR_FETCHING_FIELDS",
};
export class FeedbackRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getQuestions(datasetId: string) {
    try {
      const { data } = await this.axios.get(
        `/v1/datasets/${datasetId}/questions`
      );

      return data;
    } catch (err) {
      throw {
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_QUESTIONS,
      };
    }
  }
  async getFields(datasetId: string) {
    try {
      const { data } = await this.axios.get(`/v1/datasets/${datasetId}/fields`);

      return data;
    } catch (err) {
      throw {
        response: TYPE_OF_FEEDBACK.ERROR_FETCHING_FIELDS,
      };
    }
  }
}
