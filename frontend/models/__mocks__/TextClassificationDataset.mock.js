module.exports = {
  query: () => {
    return {
      whereId: () => {
        return {
          first: () => {
            return {};
          },
        };
      },
    };
  },
};
