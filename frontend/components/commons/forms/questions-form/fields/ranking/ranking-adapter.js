import { isNil } from "lodash";

export const adaptQuestionsToSlots = ({ options }) => {
  const slots = options.map((_, index) => {
    const id = index + 1;
    const items = options.filter((option) => option.rank == id);

    return {
      rank: id,
      items,
    };
  });

  const questions = options.filter((o) => isNil(o.rank));

  const getRanking = (option) => {
    return slots.find((slot) =>
      slot.items.some((item) => item.value === option.value)
    )?.rank;
  };

  const moveQuestionFromQuestionsToSlots = (questionToMove, slot) => {
    if (slot.items.some((question) => question.value === questionToMove.value))
      return;

    slot.items.push(questionToMove);

    const getIndexInQuestions = questions.findIndex(
      (question) => question.value === questionToMove.value
    );
    questions.splice(getIndexInQuestions, 1);
  };

  const moveQuestionsBetweenSlots = (questionToMove, slotTo) => {
    const slotFrom = slots.find((slot) =>
      slot.items.some((item) => item.value === questionToMove.value)
    );
    const getIndexOfElement = slotFrom.items.findIndex(
      (item) => item.value === questionToMove.value
    );
    slotFrom.items.splice(getIndexOfElement, 1);

    slotTo.items.push(questionToMove);
  };

  const moveQuestionToSlot = (questionToMove, slotTo) => {
    const existsAsAQuestion = questions.some(
      (q) => q.value === questionToMove.value
    );

    if (existsAsAQuestion) {
      moveQuestionFromQuestionsToSlots(questionToMove, slotTo);
    } else {
      moveQuestionsBetweenSlots(questionToMove, slotTo);
    }
  };

  return {
    slots,
    questions,
    getRanking,
    moveQuestionToSlot,
  };
};
