import { useFeedback } from "~/v1/infrastructure/FeedbackStorage";

export const useQuestionFormViewModel = () => {
  const feedbackTask = useFeedback();
  const updateRecord = (record) => {
    const feedback = feedbackTask.get();
    feedback.updateRecord(record);
    feedbackTask.save(feedback);
  };
  return { updateRecord };
};
