import { useFeedback } from "~/v1/infrastructure/FeedbackStorage";

export const useQuestionFormViewModel = () => {
  const feedbackTask = useFeedback();

  const updateResponse = (response) => {
    const feedback = feedbackTask.get();

    feedback.updateResponse(response);

    feedbackTask.save(feedback);
  };

  const addResponse = (response) => {
    const feedback = feedbackTask.get();

    feedback.addResponse(response);

    feedbackTask.save(feedback);
  };

  const clearRecord = (recordId: string, status: string) => {
    const feedback = feedbackTask.get();

    feedback.clearRecord(recordId, status);

    feedbackTask.save(feedback);
  };

  return {
    feedback: feedbackTask.state,
    updateResponse,
    addResponse,
    clearRecord,
  };
};
