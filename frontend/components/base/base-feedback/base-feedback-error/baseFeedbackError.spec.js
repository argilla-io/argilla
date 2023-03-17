import { shallowMount } from "@vue/test-utils";
import BaseFeedBackErrorComponent from "./BaseFeedbackError.component";

let wrapper = null;
const options = {
  stubs: ["BaseButton"],
  propsData: {
    message: "This is the message to show in the feedbackError component",
    buttonLabels: null,
  },
};

const spyOnClickMethod = jest.spyOn(
  BaseFeedBackErrorComponent.methods,
  "onClick"
);

beforeEach(() => {
  wrapper = shallowMount(BaseFeedBackErrorComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("BaseFeedbackErrorComponent", () => {
  it("render the component", async () => {
    expect(wrapper.is(BaseFeedBackErrorComponent)).toBe(true);
    isClassExist("feedback-wrapper");
    isMessageExistAndisMessageContentRendered();
    isClassExist("buttons-area", false);
    isClassExist("button", false);
  });
  it("render 1 button", async () => {
    setButtonsPropsAndCheckIfButtonsAreRendered([
      { label: "button1", value: "BUTTON_1" },
    ]);
  });
  it("render 2 buttons", () => {
    setButtonsPropsAndCheckIfButtonsAreRendered([
      { label: "button1", value: "BUTTON_1" },
      { label: "button2", value: "BUTTON_2" },
    ]);
  });
  it("emit on click", async () => {
    const buttonLabels = [
      { label: "button1", value: "BUTTON_1" },
      { label: "button2", value: "BUTTON_2" },
    ];

    await wrapper.setProps({
      buttonLabels,
    });

    expect(wrapper.findAll(".button")).toHaveLength(buttonLabels.length);
    buttonLabels.forEach((buttonLabel, index) => {
      testIfButtonExistAndIfOnClickMethodIsFired(buttonLabel, index);
    });
  });
});

const testIfButtonExistAndIfOnClickMethodIsFired = async (
  buttonLabel,
  eventNumber
) => {
  const button = wrapper.findComponent(`#${buttonLabel.label}`);
  expect(button.exists()).toBe(true);
  await button.vm.$emit("on-click");
  await wrapper.vm.$nextTick();
  expect(spyOnClickMethod).toHaveBeenCalled();
  expect(spyOnClickMethod).toHaveBeenCalledWith(buttonLabel.value);
  expect(wrapper.emitted("on-click")[eventNumber]).toEqual([buttonLabel.value]);
};

const setButtonsPropsAndCheckIfButtonsAreRendered = async (buttonLabels) => {
  buttonLabels.forEach(async ({ label }) => isIdExist(label, false));

  await wrapper.setProps({
    buttonLabels,
  });

  buttonLabels.forEach(async ({ label }) => isIdExist(label));
};

const isMessageExistAndisMessageContentRendered = () => {
  isClassExist("message");
  expect(wrapper.find(".message").text()).toBe(options.propsData.message);
};

const isClassExist = async (className, isExist = true) => {
  expect(wrapper.find(`.${className}`).exists()).toBe(isExist);
};
const isIdExist = async (id, isExist = true) => {
  expect(wrapper.find(`#${id}`).exists()).toBe(isExist);
};
