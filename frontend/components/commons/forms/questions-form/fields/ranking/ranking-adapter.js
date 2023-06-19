export const adaptQuestionsToSots = ({ options }) => {
  const slots = options.map((_, index) => {
    const id = index + 1;
    return {
      ranking: id,
      items: [],
    };
  });

  const questions = options.map((o) => o);

  const getRanking = (option) => {
    return slots.find((slot) =>
      slot.items.some((item) => item.value === option.value)
    )?.ranking;
  };

  return {
    slots,
    questions,
    getRanking,
  };
};
