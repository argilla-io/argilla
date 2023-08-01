import { shallowMount } from "@vue/test-utils";
import RecordFeedbackTaskComponent from "./RecordFeedbackTask.component";
import { createTextFieldMock } from "~/v1/domain/entities/__mocks__/field/mocks";

const StatusTagComponentStub = {
  name: "StatusTagComponent",
  template: "<div />",
  props: ["title"],
};

const TextFieldComponentStub = {
  name: "TextFieldComponent",
  template: "<div />",
  props: ["title", "fieldText", "useMarkdown"],
};

describe("RecordFeedbackTaskComponent", () => {
  it("render the component with ONE textFieldComponent", () => {
    const options = {
      stubs: {
        StatusTag: StatusTagComponentStub,
        TextFieldComponent: TextFieldComponentStub,
      },
      propsData: {
        recordStatus: "PENDING",
        fields: [createTextFieldMock("1")],
      },
    };

    const wrapper = shallowMount(RecordFeedbackTaskComponent, options);

    expect(wrapper.is(RecordFeedbackTaskComponent)).toBe(true);
    const StatusTagWrapper = wrapper.findComponent(StatusTagComponentStub);
    expect(StatusTagWrapper.exists()).toBe(true);

    const TextFieldComponents = wrapper.findAllComponents(
      TextFieldComponentStub
    );
    expect(TextFieldComponents.length).toBe(1);
  });

  it("render the component with TWO textFieldComponent", async () => {
    const options = {
      stubs: {
        StatusTag: StatusTagComponentStub,
        TextFieldComponent: TextFieldComponentStub,
      },
      propsData: {
        recordStatus: "PENDING",
        fields: [createTextFieldMock("1"), createTextFieldMock("2")],
      },
    };

    const wrapper = shallowMount(RecordFeedbackTaskComponent, options);
    await wrapper.vm.$nextTick();
    expect(wrapper.is(RecordFeedbackTaskComponent)).toBe(true);

    const StatusTagWrapper = wrapper.findComponent(StatusTagComponentStub);
    expect(StatusTagWrapper.exists()).toBe(true);

    const TextFieldComponents = wrapper.findAllComponents(
      TextFieldComponentStub
    );
    expect(TextFieldComponents.length).toBe(2);
  });
});
