import { shallowMount } from "@vue/test-utils";
import LabelSelectionComponent from "./LabelSelection.component";

let wrapper = null;
const options = {
  stubs: ["SearchLabelComponent", "BaseTooltip"],
  propsData: {
    componentId: `componentId`,
    options: [],
    maxOptionsToShowBeforeCollapse: 0,
  },
};
beforeEach(() => {
  wrapper = shallowMount(LabelSelectionComponent, options);
});

afterEach(() => {
  wrapper.destroy();
  window.questionSettings["componentId"].isExpandedLabelQuestions = false;
});

describe("LabelSelectionComponent in Single Selection mode", () => {
  it("render the component", () => {
    expect(wrapper.is(LabelSelectionComponent)).toBe(true);

    expect(wrapper.vm.showSearch).toBe(false);
    expect(wrapper.vm.multiple).toBe(false);
    expect(wrapper.vm.searchInput).toBe(``);
    expect(wrapper.vm.showSearch).toBe(false);
    expect(wrapper.vm.showCollapseButton).toBe(false);
    expect(wrapper.vm.searchRef).toBe(`componentIdSearchFilterRef`);

    const searchWrapper = wrapper.findComponent({
      name: "SearchLabelComponent",
    });
    const showLessButtonWrapper = wrapper.findComponent({
      ref: "showLessButtonRef",
    });
    const inputsAreaWrapper = wrapper.findComponent({ ref: "inputsAreaRef" });

    expect(searchWrapper.exists()).toBe(false);
    expect(showLessButtonWrapper.exists()).toBe(false);
    expect(inputsAreaWrapper.exists()).toBe(false);
  });
  it("render one checkbox if there is one items in options props", async () => {
    const options = [
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: false,
      },
    ];

    await wrapper.setProps({
      options,
      maxOptionsToShowBeforeCollapse: 1,
    });

    // by default it's a single selection
    expect(wrapper.vm.multiple).toBe(false);

    // by default there is no search
    const searchWrapper = wrapper.findComponent({
      name: "SearchLabelComponent",
    });
    expect(searchWrapper.exists()).toBe(false);

    // by default there is no collapse button
    const showLessButtonWrapper = wrapper.findComponent({
      ref: "showLessButtonRef",
    });
    expect(showLessButtonWrapper.exists()).toBe(false);

    const inputsAreaWrapper = wrapper.findComponent({ ref: "inputsAreaRef" });
    expect(inputsAreaWrapper.exists()).toBe(true);
    const inputWrapper = wrapper.findComponent("#sentiment_positive");
    expect(inputWrapper.exists()).toBe(true);

    const labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("round");
    expect(labelsWrapper.length).toBe(1);
  });
  it("render two checkbox if there is two items in options props", async () => {
    const options = [
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: false,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
    ];

    await wrapper.setProps({
      options,
      maxOptionsToShowBeforeCollapse: 2,
    });

    // by default it's a single selection
    expect(wrapper.vm.multiple).toBe(false);

    // by default there is no search
    const searchWrapper = wrapper.findComponent({
      name: "SearchLabelComponent",
    });
    expect(searchWrapper.exists()).toBe(false);

    // by default there is no collapse button
    const showLessButtonWrapper = wrapper.findComponent({
      ref: "showLessButtonRef",
    });
    expect(showLessButtonWrapper.exists()).toBe(false);

    const inputsAreaWrapper = wrapper.findComponent({ ref: "inputsAreaRef" });
    expect(inputsAreaWrapper.exists()).toBe(true);
    const input1Wrapper = wrapper.findComponent("#sentiment_positive");
    expect(input1Wrapper.exists()).toBe(true);
    const input2Wrapper = wrapper.findComponent("#sentiment_very_positive");
    expect(input2Wrapper.exists()).toBe(true);

    const labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("round");
    expect(labelsWrapper.at(1).classes()).toContain("round");
    expect(labelsWrapper.length).toBe(2);
  });
  it("render three checkbox if there is three items in options props", async () => {
    const options = [
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: false,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ];

    await wrapper.setProps({
      options,
      maxOptionsToShowBeforeCollapse: 3,
    });

    // by default it's a single selection
    expect(wrapper.vm.multiple).toBe(false);

    // by default there is no search
    const searchWrapper = wrapper.findComponent({
      name: "SearchLabelComponent",
    });
    expect(searchWrapper.exists()).toBe(false);

    // by default there is no collapse button
    const showLessButtonWrapper = wrapper.findComponent({
      ref: "showLessButtonRef",
    });
    expect(showLessButtonWrapper.exists()).toBe(false);

    const inputsAreaWrapper = wrapper.findComponent({ ref: "inputsAreaRef" });
    expect(inputsAreaWrapper.exists()).toBe(true);
    const input1Wrapper = wrapper.findComponent("#sentiment_positive");
    expect(input1Wrapper.exists()).toBe(true);
    const input2Wrapper = wrapper.findComponent("#sentiment_very_positive");
    expect(input2Wrapper.exists()).toBe(true);
    const input3Wrapper = wrapper.findComponent("#sentiment_negative");
    expect(input3Wrapper.exists()).toBe(true);

    const labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("round");
    expect(labelsWrapper.at(1).classes()).toContain("round");
    expect(labelsWrapper.at(2).classes()).toContain("round");
    expect(labelsWrapper.length).toBe(3);
  });
  it("update the flag 'isSelected' of the corresponding checkbox option when user click (no items have been selected)", async () => {
    const options = [
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: false,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ];

    await wrapper.setProps({
      options,
      maxOptionsToShowBeforeCollapse: 3,
    });

    // by default it's a single selection
    expect(wrapper.vm.multiple).toBe(false);

    expect(wrapper.vm.options).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: false,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
    const checkbox = wrapper.find("#sentiment_positive");
    await checkbox.setChecked();
    expect(checkbox.element.checked).toBeTruthy();
    expect(wrapper.vm.options).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
  });
  it("update the flag 'isSelected' of the corresponding checkbox option when user click (one item have been selected)", async () => {
    const options = [
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ];

    await wrapper.setProps({
      options,
      maxOptionsToShowBeforeCollapse: 3,
    });

    // by default it's a single selection
    expect(wrapper.vm.multiple).toBe(false);

    expect(wrapper.vm.options).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
    const checkbox = wrapper.find("#sentiment_very_positive");
    await checkbox.setChecked();
    expect(checkbox.element.checked).toBeTruthy();
    expect(wrapper.vm.options).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: false,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: true,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
  });
  it("filter the options when user write in the search input", async () => {
    const options = [
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ];

    await wrapper.setProps({
      options,
      maxOptionsToShowBeforeCollapse: 3,
      showSearch: true,
    });

    // by default it's a single selection
    expect(wrapper.vm.multiple).toBe(false);

    const searchWrapper = wrapper.findComponent({ ref: "searchComponentRef" });
    expect(searchWrapper.exists()).toBe(false);

    await wrapper.setData({ searchInput: "" });
    expect(wrapper.vm.filteredOptions).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
    let labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("round");
    expect(labelsWrapper.at(1).classes()).toContain("round");
    expect(labelsWrapper.at(2).classes()).toContain("round");
    expect(labelsWrapper.length).toBe(3);

    await wrapper.setData({ searchInput: "Very" });
    expect(wrapper.vm.filteredOptions).toStrictEqual([
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
    ]);
    labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("round");
    expect(labelsWrapper.length).toBe(1);

    await wrapper.setData({ searchInput: "I'm blue daboudi dabouda" });
    expect(wrapper.vm.filteredOptions).toStrictEqual([]);
    labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.length).toBe(0);

    await wrapper.setData({ searchInput: "" });
    expect(wrapper.vm.filteredOptions).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
    labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("round");
    expect(labelsWrapper.at(1).classes()).toContain("round");
    expect(labelsWrapper.at(2).classes()).toContain("round");
    expect(labelsWrapper.length).toBe(3);
  });
  it("collapse the list of labels when user click on collapse button", async () => {
    const options = [
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ];

    await wrapper.setProps({
      options,
      maxOptionsToShowBeforeCollapse: 2,
      showSearch: true,
    });

    const showLessButtonWrapper = wrapper.findComponent({
      ref: "showLessButtonRef",
    });
    expect(showLessButtonWrapper.exists()).toBe(true);
    expect(wrapper.vm.isExpanded).toBe(false);
    expect(showLessButtonWrapper.text()).toBe("+1");
    expect(wrapper.vm.visibleOptions).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
    ]);
    let labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("round");
    expect(labelsWrapper.at(1).classes()).toContain("round");
    expect(labelsWrapper.length).toBe(2);

    await showLessButtonWrapper.trigger("click");
    expect(wrapper.vm.isExpanded).toBe(true);
    expect(showLessButtonWrapper.text()).toBe("#less#");
    expect(wrapper.vm.visibleOptions).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
    labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("round");
    expect(labelsWrapper.at(1).classes()).toContain("round");
    expect(labelsWrapper.at(2).classes()).toContain("round");
    expect(labelsWrapper.length).toBe(3);
  });
});

describe("LabelSelectionComponent in Multi Selection mode", () => {
  it("render three checkbox if there is three items in options props", async () => {
    const options = [
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: false,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ];

    await wrapper.setProps({
      options,
      maxOptionsToShowBeforeCollapse: 3,
      multiple: true,
    });

    // by default it's a single selection
    expect(wrapper.vm.multiple).toBe(true);

    // by default there is no search
    const searchWrapper = wrapper.findComponent({
      name: "SearchLabelComponent",
    });
    expect(searchWrapper.exists()).toBe(false);

    // by default there is no collapse button
    const showLessButtonWrapper = wrapper.findComponent({
      ref: "showLessButtonRef",
    });
    expect(showLessButtonWrapper.exists()).toBe(false);

    const inputsAreaWrapper = wrapper.findComponent({ ref: "inputsAreaRef" });
    expect(inputsAreaWrapper.exists()).toBe(true);
    const input1Wrapper = wrapper.findComponent("#sentiment_positive");
    expect(input1Wrapper.exists()).toBe(true);
    const input2Wrapper = wrapper.findComponent("#sentiment_very_positive");
    expect(input2Wrapper.exists()).toBe(true);
    const input3Wrapper = wrapper.findComponent("#sentiment_negative");
    expect(input3Wrapper.exists()).toBe(true);

    const labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("square");
    expect(labelsWrapper.at(1).classes()).toContain("square");
    expect(labelsWrapper.at(2).classes()).toContain("square");
    expect(labelsWrapper.length).toBe(3);
  });
  it("update the flag 'isSelected' of the corresponding checkbox option when user click (no items have been selected)", async () => {
    const options = [
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: false,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ];

    await wrapper.setProps({
      options,
      maxOptionsToShowBeforeCollapse: 3,
      multiple: true,
    });

    // by default it's a single selection
    expect(wrapper.vm.multiple).toBe(true);

    expect(wrapper.vm.options).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: false,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
    const checkbox = wrapper.find("#sentiment_positive");
    await checkbox.setChecked();
    expect(checkbox.element.checked).toBeTruthy();
    expect(wrapper.vm.options).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
  });
  it("update the flag 'isSelected' of the corresponding checkbox option when user click (one item have been selected)", async () => {
    const options = [
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ];

    await wrapper.setProps({
      options,
      maxOptionsToShowBeforeCollapse: 3,
      multiple: true,
    });

    // by default it's a single selection
    expect(wrapper.vm.multiple).toBe(true);

    expect(wrapper.vm.options).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
    const checkbox = wrapper.find("#sentiment_very_positive");
    await checkbox.setChecked();
    expect(checkbox.element.checked).toBeTruthy();
    expect(wrapper.vm.options).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: true,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
  });
  it("filter the options when user write in the search input", async () => {
    const options = [
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ];

    await wrapper.setProps({
      options,
      maxOptionsToShowBeforeCollapse: 3,
      multiple: true,
      showSearch: true,
    });

    // by default it's a single selection
    expect(wrapper.vm.multiple).toBe(true);

    const searchWrapper = wrapper.findComponent({ ref: "searchComponentRef" });
    expect(searchWrapper.exists()).toBe(false);

    await wrapper.setData({ searchInput: "" });
    expect(wrapper.vm.filteredOptions).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
    let labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("square");
    expect(labelsWrapper.at(1).classes()).toContain("square");
    expect(labelsWrapper.at(2).classes()).toContain("square");
    expect(labelsWrapper.length).toBe(3);

    await wrapper.setData({ searchInput: "Very" });
    expect(wrapper.vm.filteredOptions).toStrictEqual([
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
    ]);
    labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("square");
    expect(labelsWrapper.length).toBe(1);

    await wrapper.setData({ searchInput: "I'm blue daboudi dabouda" });
    expect(wrapper.vm.filteredOptions).toStrictEqual([]);
    labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.length).toBe(0);

    await wrapper.setData({ searchInput: "" });
    expect(wrapper.vm.filteredOptions).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
    labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("square");
    expect(labelsWrapper.at(1).classes()).toContain("square");
    expect(labelsWrapper.at(2).classes()).toContain("square");
    expect(labelsWrapper.length).toBe(3);
  });
  it("collapse the list of labels when user click on collapse button", async () => {
    const options = [
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ];

    await wrapper.setProps({
      options,
      multiple: true,
      maxOptionsToShowBeforeCollapse: 2,
      showSearch: true,
    });

    const showLessButtonWrapper = wrapper.findComponent({
      ref: "showLessButtonRef",
    });
    expect(showLessButtonWrapper.exists()).toBe(true);
    expect(wrapper.vm.isExpanded).toBe(false);
    expect(showLessButtonWrapper.text()).toBe("+1");
    expect(wrapper.vm.visibleOptions).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
    ]);
    let labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("square");
    expect(labelsWrapper.at(1).classes()).toContain("square");
    expect(labelsWrapper.length).toBe(2);

    await showLessButtonWrapper.trigger("click");
    expect(wrapper.vm.isExpanded).toBe(true);
    expect(showLessButtonWrapper.text()).toBe("#less#");
    expect(wrapper.vm.visibleOptions).toStrictEqual([
      {
        id: "sentiment_positive",
        text: "Positive",
        value: "positive",
        isSelected: true,
      },
      {
        id: "sentiment_very_positive",
        text: "Very Positive",
        value: "very_positive",
        isSelected: false,
      },
      {
        id: "sentiment_negative",
        text: "Negative",
        value: "negative",
        isSelected: false,
      },
    ]);
    labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("square");
    expect(labelsWrapper.at(1).classes()).toContain("square");
    expect(labelsWrapper.at(2).classes()).toContain("square");
    expect(labelsWrapper.length).toBe(3);
  });
});
