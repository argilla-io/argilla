import { shallowMount } from "@vue/test-utils";
import RatingMonoSelectionComponent from "./RatingMonoSelection.component";

let wrapper = null;
const options = {
  stubs: ["BaseTooltip"],
  propsData: {
    options: [
      { id: "helpfulness_reply_1_1", value: 1, text: 1, isSelected: false },
      { id: "helpfulness_reply_1_2", value: 2, text: 2, isSelected: false },
      { id: "helpfulness_reply_1_3", value: 3, text: 3, isSelected: false },
      { id: "helpfulness_reply_1_4", value: 4, text: 4, isSelected: false },
      { id: "helpfulness_reply_1_5", value: 5, text: 5, isSelected: false },
    ],
  },
};
beforeEach(() => {
  wrapper = shallowMount(RatingMonoSelectionComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("RatingMonoSelectionComponent", () => {
  it("render the component and the rating options", () => {
    expect(wrapper.is(RatingMonoSelectionComponent)).toBe(true);

    const labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("label-text");
    expect(labelsWrapper.at(0).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(0).text()).toBe("1");

    expect(labelsWrapper.at(1).classes()).toContain("label-text");
    expect(labelsWrapper.at(1).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(1).text()).toBe("2");

    expect(labelsWrapper.at(2).classes()).toContain("label-text");
    expect(labelsWrapper.at(2).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(2).text()).toBe("3");

    expect(labelsWrapper.at(3).classes()).toContain("label-text");
    expect(labelsWrapper.at(3).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(3).text()).toBe("4");

    expect(labelsWrapper.at(4).classes()).toContain("label-text");
    expect(labelsWrapper.at(4).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(4).text()).toBe("5");

    expect(labelsWrapper.length).toBe(5);
  });
  it("update the flag 'isSelected' of the corresponding checkbox option when user click (no items have been selected)", async () => {
    const checkbox1 = wrapper.find("#helpfulness_reply_1_1");
    const checkbox2 = wrapper.find("#helpfulness_reply_1_2");
    const checkbox3 = wrapper.find("#helpfulness_reply_1_3");
    const checkbox4 = wrapper.find("#helpfulness_reply_1_4");
    const checkbox5 = wrapper.find("#helpfulness_reply_1_5");

    expect(wrapper.vm.options).toStrictEqual([
      { id: "helpfulness_reply_1_1", value: 1, text: 1, isSelected: false },
      { id: "helpfulness_reply_1_2", value: 2, text: 2, isSelected: false },
      { id: "helpfulness_reply_1_3", value: 3, text: 3, isSelected: false },
      { id: "helpfulness_reply_1_4", value: 4, text: 4, isSelected: false },
      { id: "helpfulness_reply_1_5", value: 5, text: 5, isSelected: false },
    ]);

    await checkbox1.setChecked();

    expect(wrapper.vm.options).toStrictEqual([
      { id: "helpfulness_reply_1_1", value: 1, text: 1, isSelected: true },
      { id: "helpfulness_reply_1_2", value: 2, text: 2, isSelected: false },
      { id: "helpfulness_reply_1_3", value: 3, text: 3, isSelected: false },
      { id: "helpfulness_reply_1_4", value: 4, text: 4, isSelected: false },
      { id: "helpfulness_reply_1_5", value: 5, text: 5, isSelected: false },
    ]);

    expect(checkbox1.element.checked).toBeTruthy();
    expect(checkbox2.element.checked).toBeFalsy();
    expect(checkbox3.element.checked).toBeFalsy();
    expect(checkbox4.element.checked).toBeFalsy();
    expect(checkbox5.element.checked).toBeFalsy();

    const labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).toContain("label-active");
    expect(labelsWrapper.at(1).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(2).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(3).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(4).classes()).not.toContain("label-active");
    expect(labelsWrapper.length).toBe(5);
  });
  it("update the flag 'isSelected' of the corresponding checkbox which have been selected previously => unselect a select checkbox", async () => {
    const checkbox1 = wrapper.find("#helpfulness_reply_1_1");
    const checkbox2 = wrapper.find("#helpfulness_reply_1_2");
    const checkbox3 = wrapper.find("#helpfulness_reply_1_3");
    const checkbox4 = wrapper.find("#helpfulness_reply_1_4");
    const checkbox5 = wrapper.find("#helpfulness_reply_1_5");

    await checkbox1.setChecked(true);
    await checkbox1.setChecked(false);

    expect(checkbox1.element.checked).toBeFalsy();
    expect(checkbox2.element.checked).toBeFalsy();
    expect(checkbox3.element.checked).toBeFalsy();
    expect(checkbox4.element.checked).toBeFalsy();
    expect(checkbox5.element.checked).toBeFalsy();

    const labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(1).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(2).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(3).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(4).classes()).not.toContain("label-active");
    expect(labelsWrapper.length).toBe(5);
  });
  it("update the flag 'isSelected' of the corresponding checkbox which have been selected previously => ensure that only one checkbox is checked at a time", async () => {
    const checkbox1 = wrapper.find("#helpfulness_reply_1_1");
    const checkbox2 = wrapper.find("#helpfulness_reply_1_2");
    const checkbox3 = wrapper.find("#helpfulness_reply_1_3");
    const checkbox4 = wrapper.find("#helpfulness_reply_1_4");
    const checkbox5 = wrapper.find("#helpfulness_reply_1_5");

    await checkbox1.setChecked(true);
    await checkbox5.setChecked(true);

    expect(checkbox1.element.checked).toBeFalsy();
    expect(checkbox2.element.checked).toBeFalsy();
    expect(checkbox3.element.checked).toBeFalsy();
    expect(checkbox4.element.checked).toBeFalsy();
    expect(checkbox5.element.checked).toBeTruthy();

    const labelsWrapper = wrapper.findAll("label");
    expect(labelsWrapper.at(0).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(1).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(2).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(3).classes()).not.toContain("label-active");
    expect(labelsWrapper.at(4).classes()).toContain("label-active");
    expect(labelsWrapper.length).toBe(5);
  });
});
