import { shallowMount } from "@vue/test-utils";
import MultiLabelComponent from "./MultiLabel.component";

const QuestionHeaderComponentStub = {
  name: "QuestionHeaderComponent",
  template: "<div />",
  props: ["title", "isRequired", "tooltipMessage"],
};
const LabelSelectionComponentStub = {
  name: "LabelSelectionComponent",
  template: "<div />",
  props: ["multiple", "componentId", "maxOptionsToShowBeforeCollapse"],
};

describe("MultiLabelComponent", () => {
  it("render by default the QuestionHeader and the LabelSelectionComponent", () => {
    const options = initOptionsToMount({
      propsOptions: [
        {
          id: "sentiment_positive",
          value: "positive",
          text: "Positive",
          isSelected: false,
        },
        {
          id: "sentiment_very_positive",
          value: "very_positive",
          text: "Very Positive",
          isSelected: false,
        },
        {
          id: "sentiment_negative",
          value: "negative",
          text: "Negative",
          isSelected: false,
        },
      ],
    });
    const wrapper = shallowMount(MultiLabelComponent, options);

    expect(wrapper.is(MultiLabelComponent)).toBe(true);

    const QuestionHeaderWrapper = wrapper.findComponent({
      name: "QuestionHeaderComponent",
    });
    expect(QuestionHeaderWrapper.exists()).toBe(true);

    const labelSelectionWrapper = wrapper.findComponent({
      name: "LabelSelectionComponent",
    });
    expect(labelSelectionWrapper.exists()).toBe(true);

    expect(wrapper.vm.options).toStrictEqual([
      {
        id: "sentiment_positive",
        value: "positive",
        text: "Positive",
        isSelected: false,
      },
      {
        id: "sentiment_very_positive",
        value: "very_positive",
        text: "Very Positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        value: "negative",
        text: "Negative",
        isSelected: false,
      },
    ]);
    expect(wrapper.vm.maxOptionsToShowBeforeCollapse).toBe(-1);

    // test what we pass to children components
    expect(
      wrapper.findComponent(QuestionHeaderComponentStub).props("title")
    ).toBe(wrapper.vm.title);
    expect(
      wrapper.findComponent(QuestionHeaderComponentStub).props("isRequired")
    ).toBe(wrapper.vm.isRequired);
    expect(
      wrapper.findComponent(QuestionHeaderComponentStub).props("tooltipMessage")
    ).toBe(wrapper.vm.description);

    expect(
      wrapper.findComponent(LabelSelectionComponentStub).props("multiple")
    ).toBe(true);
    expect(
      wrapper.findComponent(LabelSelectionComponentStub).props("componentId")
    ).toBe(wrapper.vm.questionId);
    expect(
      wrapper
        .findComponent(LabelSelectionComponentStub)
        .props("maxOptionsToShowBeforeCollapse")
    ).toBe(wrapper.vm.maxOptionsToShowBeforeCollapse);
  });
  it("update the maxOptionsToShowBeforeCollapse depending of the value of the props visibleOptions", async () => {
    const options = initOptionsToMount({
      propsOptions: [
        {
          id: "sentiment_positive",
          value: "positive",
          text: "Positive",
          isSelected: false,
        },
        {
          id: "sentiment_very_positive",
          value: "very_positive",
          text: "Very Positive",
          isSelected: false,
        },
        {
          id: "sentiment_negative",
          value: "negative",
          text: "Negative",
          isSelected: false,
        },
      ],
    });
    const wrapper = shallowMount(MultiLabelComponent, options);

    expect(wrapper.vm.maxOptionsToShowBeforeCollapse).toBe(-1);
    await wrapper.setProps({ visibleOptions: 12 });
    expect(wrapper.vm.maxOptionsToShowBeforeCollapse).toBe(12);

    const QuestionHeaderWrapper = wrapper.findComponent({
      name: "QuestionHeaderComponent",
    });
    expect(QuestionHeaderWrapper.exists()).toBe(true);

    const labelSelectionWrapper = wrapper.findComponent({
      name: "LabelSelectionComponent",
    });
    expect(labelSelectionWrapper.exists()).toBe(true);

    // test what we pass to children components
    expect(
      wrapper.findComponent(QuestionHeaderComponentStub).props("title")
    ).toBe(wrapper.vm.title);
    expect(
      wrapper.findComponent(QuestionHeaderComponentStub).props("isRequired")
    ).toBe(wrapper.vm.isRequired);
    expect(
      wrapper.findComponent(QuestionHeaderComponentStub).props("tooltipMessage")
    ).toBe(wrapper.vm.description);

    expect(
      wrapper.findComponent(LabelSelectionComponentStub).props("multiple")
    ).toBe(true);
    expect(
      wrapper.findComponent(LabelSelectionComponentStub).props("componentId")
    ).toBe(wrapper.vm.questionId);
    expect(
      wrapper
        .findComponent(LabelSelectionComponentStub)
        .props("maxOptionsToShowBeforeCollapse")
    ).toBe(wrapper.vm.maxOptionsToShowBeforeCollapse);
  });
});

const initOptionsToMount = ({ propsOptions }) => {
  const options = {
    stubs: {
      LabelSelectionComponent: LabelSelectionComponentStub,
      QuestionHeaderComponent: QuestionHeaderComponentStub,
    },
    directives: {
      "optional-field"() {
        // this directive is used to show '(optional)' at the end of a question optional
      },
      tooltip() {
        // this directive is used to show a tooltip
      },
    },
    propsData: {
      questionId: "questionId",
      title: "This is the question",
      options: propsOptions,
      isRequired: false,
      tooltipMessage: null,
      visibleOptions: null,
    },
  };

  return options;
};
