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
        allow: true,
        active: true,
      },
      {
        id: "discard",
        name: "Discard",
        allow: true,
        active: true,
      },
      {
        id: "clear",
        name: "Clear",
        allow: false,
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
  it("expect to show validate button active", async () => {
    testIfButtonIsDisabled("validate", undefined);
  });
  it("expect to show discard button active", async () => {
    testIfButtonIsDisabled("discard", undefined);
  });
  it("expect to emit validate on click validate button", async () => {
    testIfEmittedIsCorrect("validate");
  });
  it("expect to emit discard on click discard button", async () => {
    testIfEmittedIsCorrect("discard");
  });
  it("expect not to render clear button", async () => {
    const clearButton = wrapper.find(`.record__actions-button--clear`);
    expect(clearButton.exists()).toBe(false);
  });
});

const testIfButtonIsDisabled = async (button, disabled) => {
  const actionButton = wrapper.find(`.record__actions-button--${button}`);
  expect(actionButton.attributes().disabled).toBe(disabled);
};
const testIfEmittedIsCorrect = async (button) => {
  wrapper.find(`.record__actions-button--${button}`).vm.$emit("click");
  expect(wrapper.emitted()).toHaveProperty(button);
};
