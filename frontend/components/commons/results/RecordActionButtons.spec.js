import { shallowMount } from "@vue/test-utils";
import RecordActionButtons from "./RecordActionButtons";
import BaseButton from "@/components/base/BaseButton";

let wrapper = null;
const options = {
  stubs: {
    "base-button": BaseButton,
  },
  propsData: {
    actions: [
      {
        id: "validate",
        name: "Validate",
        active: true,
      },
      {
        id: "discard",
        name: "Discard",
        active: true,
      },
      {
        id: "clear",
        name: "Clear",
        active: false,
      },
    ],
  },
};
beforeEach(() => {
  wrapper = shallowMount(RecordActionButtons, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("RecordActionButtonsComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(RecordActionButtons)).toBe(true);
  });
  it("expect to render validate button", async () => {
    testIfButtonRender("validate", true);
  });
  it("expect to render discard button", async () => {
    testIfButtonRender("discard", true);
  });
  it("expect to not render clear button", async () => {
    testIfButtonRender("clear", false);
  });
  it("expect to emit validate on click validate button", async () => {
    testIfEmittedIsCorrect("validate");
  });
  it("expect to emit discard on click discard button", async () => {
    testIfEmittedIsCorrect("discard");
  });
});

const testIfButtonRender = async (button, render) => {
  const actionButton = wrapper.find(`.record__actions-button--${button}`);
  expect(actionButton.exists()).toBe(render);
};
const testIfEmittedIsCorrect = async (button) => {
  wrapper.find(`.record__actions-button--${button}`).vm.$emit("click");
  expect(wrapper.emitted()).toHaveProperty(button);
};
