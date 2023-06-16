export const factoryRanking = ({ options }) => {
  const slots = options.map((_, index) => {
    const id = index + 1;
    return {
      index: id,
      name: `#${id}`,
      items: [],
    };
  });

  const questions = options.map((option, index) => ({
    id: index + 1,
    name: option.text,
  }));

  return {
    slots,
    questions,
  };
};
