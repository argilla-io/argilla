import { shallowMount } from "@vue/test-utils";
import BaseFeedBackComponent from "./BaseFeedback";
import BaseFeedbackErrorComponent from "./base-feedback-error/BaseFeedbackError.component";

let wrapper = null;
const options = {
  components: { BaseFeedbackErrorComponent },
  propsData: {
    feedbackInput: {
      message: null,
      buttonLabels: null,
      feedbackType: null,
    },
  },
};

beforeEach(() => {
  wrapper = shallowMount(BaseFeedBackComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("BaseFeedbackComponent", () => {
  it("not render BaseFeedbackErrorComponent component if feedbackType !=='ERROR'", async () => {
    const feedbackInput = {
      message: "This is the message",
      buttonLabels: null,
      feedbackType: null,
    };

    await wrapper.setProps({
      feedbackInput,
    });

    expect(wrapper.vm.isFeedbackError).toBe(false);
    await wrapper.vm.$nextTick();
    expect(wrapper.findComponent(BaseFeedbackErrorComponent).exists()).toBe(
      false
    );
  });
  it("render BaseFeedbackErrorComponent component if feedbackType ==='ERROR'", async () => {
    const feedbackInput = {
      message: "This is the message to show in the feedbackError component",
      buttonLabels: null,
      feedbackType: "ERROR",
    };

    await wrapper.setProps({
      feedbackInput,
    });

    expect(wrapper.vm.isFeedbackError).toBe(true);
    await wrapper.vm.$nextTick();
    expect(wrapper.findComponent(BaseFeedbackErrorComponent).exists()).toBe(
      true
    );
  });
});
