import Vue from "vue";
const getters = {};

const actions = {
  notify(_, { message, type }) {
    return Vue.$toast.open({
      message,
      type: type || "default",
    });
  },
};

export default {
  getters,
  actions,
};
