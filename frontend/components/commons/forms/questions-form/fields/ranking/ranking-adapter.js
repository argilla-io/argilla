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

  return {
    slots,
    questions,
    getRanking,
  };
};
