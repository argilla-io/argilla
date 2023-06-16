import { shallowMount } from "@vue/test-utils";
import RecordFeedbackTaskComponent from "./RecordFeedbackTask.component";

describe("RecordFeedbackTaskComponent", () => {
  it("render the component with ONE textFieldComponent", () => {
    const options = {
      stubs: ["StatusTag", "TextFieldComponent"],
      propsData: {
        recordStatus: "PENDING",
        fields: [
          {
            $id: "892ca786-d38d-4bd5-b5c6-cec01a561d21",
            id: "892ca786-d38d-4bd5-b5c6-cec01a561d21",
            name: "prompt",
            dataset_id: "528bdf17-ae8c-45ec-ada9-a75fd40ca3c3",
            order: 0,
            title: "Prompt",
            is_required: true,
            component_type: "TEXT_FIELD",
            settings: { type: "text", use_markdown: false },
            field_text: "PROMPT",
          },
        ],
      },
    };

    const wrapper = shallowMount(RecordFeedbackTaskComponent, options);

    expect(wrapper.is(RecordFeedbackTaskComponent)).toBe(true);
    const StatusTagWrapper = wrapper.findComponent({ name: "StatusTag" });

    expect(StatusTagWrapper.exists()).toBe(true);
    const TextFieldComponents = wrapper.findAllComponents({
      name: "TextFieldComponent",
    });
    expect(TextFieldComponents.length).toBe(1);
  });
  it("render the component with TWO textFieldComponent", () => {
    const options = {
      stubs: ["StatusTag", "TextFieldComponent"],
      propsData: {
        recordStatus: "PENDING",
        fields: [
          {
            $id: "892ca786-d38d-4bd5-b5c6-cec01a561d21",
            id: "892ca786-d38d-4bd5-b5c6-cec01a561d21",
            name: "prompt",
            dataset_id: "528bdf17-ae8c-45ec-ada9-a75fd40ca3c3",
            order: 0,
            title: "Prompt",
            is_required: true,
            component_type: "TEXT_FIELD",
            settings: { type: "text", use_markdown: false },
            field_text: "PROMPT",
          },
          {
            $id: "aeae41b7-334e-4f7f-9de6-4a053d739785",
            id: "aeae41b7-334e-4f7f-9de6-4a053d739785",
            name: "completion",
            dataset_id: "528bdf17-ae8c-45ec-ada9-a75fd40ca3c3",
            order: 1,
            title: "Completion",
            is_required: true,
            component_type: "TEXT_FIELD",
            settings: { type: "text", use_markdown: false },
            field_text: "COMPLETION",
          },
        ],
      },
    };

    const wrapper = shallowMount(RecordFeedbackTaskComponent, options);

    expect(wrapper.is(RecordFeedbackTaskComponent)).toBe(true);
    const StatusTagWrapper = wrapper.findComponent({ name: "StatusTag" });

    expect(StatusTagWrapper.exists()).toBe(true);
    const TextFieldComponents = wrapper.findAllComponents({
      name: "TextFieldComponent",
    });
    expect(TextFieldComponents.length).toBe(2);
  });
});
