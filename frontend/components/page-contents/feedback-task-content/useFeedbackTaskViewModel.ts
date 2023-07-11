import { useResolve } from "ts-injecty";
import { FeedbackRepository } from "@/v1/infrastructure/FeedbackRepository";
import { Feedback, Field, Question } from "@/v1/domain/entities/Feedback";
import { useFeedback } from "@/v1/infrastructure/FeedbackStorage";

export const useFeedbackTaskViewModel = () => {
  const feedbackStore = useFeedback();
  const repository = useResolve(FeedbackRepository);

  const fetch = async (datasetId: string) => {
    const [questionsFromBackend, fieldsFromBackend] = await Promise.all([
      repository.getQuestions(datasetId),
      repository.getFields(datasetId),
    ]);

    const questions = questionsFromBackend.map(
      ({
        id,
        name,
        description,
        dataset_id,
        question,
        order,
        is_required,
        settings,
        options,
        component_type,
        placeholder,
      }) => {
        return new Question(
          id,
          name,
          description,
          dataset_id,
          question,
          order,
          is_required,
          settings,
          options,
          component_type,
          placeholder
        );
      }
    );

    const fields = fieldsFromBackend.map(
      ({
        id,
        name,
        dataset_id,
        title,
        order,
        is_required,
        settings,
        component_type,
      }) => {
        return new Field(
          id,
          name,
          title,
          dataset_id,
          order,
          is_required,
          settings,
          component_type
        );
      }
    );

    return new Feedback(questions, fields);
  };

  const loadFeedback = async (datasetId: string) => {
    const feedback = await fetch(datasetId);

    feedbackStore.save(feedback);
  };
  return { feedback: feedbackStore.state, loadFeedback };
};
