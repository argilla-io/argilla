import { useResolve } from "ts-injecty";
import { FeedbackRepository } from "@/v1/infrastructure/FeedbackRepository";
import { Feedback } from "@/v1/domain/entities/Feedback";
import { useFeedback } from "@/v1/infrastructure/FeedbackStorage";

export const useFeedbackTaskViewModel = () => {
  const feedbackStore = useFeedback();
  const repository = useResolve(FeedbackRepository);

  const fetch = async (datasetId: string) => {
    const [questions, fields] = await Promise.all([
      repository.getQuestions(datasetId),
      repository.getFields(datasetId),
    ]);

    return new Feedback(questions, fields);
  };

  const loadFeedback = async (datasetId: string) => {
    const feedback = await fetch(datasetId);

    feedbackStore.save(feedback);
  };
  return { feedback: feedbackStore.state, loadFeedback };
};
