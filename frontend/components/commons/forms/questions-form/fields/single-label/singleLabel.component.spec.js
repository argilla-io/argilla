import { shallowMount } from "@vue/test-utils";
import SingleLabelComponent from "./SingleLabel.component";

let wrapper = null;
const options = {
  stubs: [
    "QuestionHeaderComponent",
    "LabelSelectionComponent",
    "BaseIconWithBadge",
  ],
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
    options: [
      {
        id: "sentiment_positive",
        value: "positive",
        text: "Positive",
        is_selected: false,
      },
      {
        id: "sentiment_very_positive",
        value: "very_positive",
        text: "Very Positive",
        is_selected: false,
      },
      {
        id: "sentiment_negative",
        value: "negative",
        text: "Negative",
        is_selected: false,
      },
      {
        id: "sentiment_negative",
        value: "negative",
        text: "Negative",
        is_selected: false,
      },
    ],
    isRequired: false,
    tooltipMessage: null,
    visibleOptions: null,
  },
};

beforeEach(() => {
  wrapper = shallowMount(SingleLabelComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("SingleLabelComponent", () => {
  it("render by default the title of the question and the LabelSelectionComponent", () => {
    expect(wrapper.is(SingleLabelComponent)).toBe(true);

    const QuestionHeaderWrapper = wrapper.findComponent({
      name: "QuestionHeaderComponent",
    });
    expect(QuestionHeaderWrapper.exists()).toBe(true);
    const labelSelectionWrapper = wrapper.findComponent({
      name: "LabelSelectionComponent",
    });
    expect(labelSelectionWrapper.exists()).toBe(true);

    expect(wrapper.vm.uniqueOptions).toStrictEqual([
      {
        id: "sentiment_positive",
        value: "positive",
        text: "Positive",
        is_selected: false,
      },
      {
        id: "sentiment_very_positive",
        value: "very_positive",
        text: "Very Positive",
        is_selected: false,
      },
      {
        id: "sentiment_negative",
        value: "negative",
        text: "Negative",
        is_selected: false,
      },
    ]);
    expect(wrapper.vm.showSearch).toBe(true);
    expect(wrapper.vm.maxOptionsToShowBeforeCollapse).toBe(-1);
  });
  it("update the maxOptionsToShowBeforeCollapse depending of the value of the props visibleOptions", async () => {
    expect(wrapper.vm.maxOptionsToShowBeforeCollapse).toBe(-1);
    await wrapper.setProps({ visibleOptions: 12 });
    expect(wrapper.vm.maxOptionsToShowBeforeCollapse).toBe(12);
  });
  it.skip("compute showSearch at false if uniqueOptions have less than OPTIONS_THRESHOLD_TO_ENABLE_SEARCH items", async () => {
    // FIXME
    await wrapper.setProps({
      options: [
        {
          id: "sentiment_positive",
          value: "positive",
          text: "Positive",
          is_selected: false,
        },
        {
          id: "sentiment_very_positive",
          value: "very_positive",
          text: "Very Positive",
          is_selected: false,
        },
      ],
    });
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.showSearch).toBe(false);
  });
});
