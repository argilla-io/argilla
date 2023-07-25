import { shallowMount } from "@vue/test-utils";
import RatingShortcutsComponent from "./RatingShortcuts";

let wrapper = null;
const options = {
  scopedSlots: {
    options: "<div></div>",
    // mocks: {
    //   options: [
    //     {
    //       id: "rating_1",
    //       value: 1,
    //       isSelected: false,
    //     },
    //     {
    //       id: "rating_2",
    //       value: 2,
    //       isSelected: false,
    //     },
    //     {
    //       id: "rating_3",
    //       value: 3,
    //       isSelected: false,
    //     },
    //     {
    //       id: "rating_4",
    //       value: 4,
    //       isSelected: false,
    //     },
    //     {
    //       id: "rating_5",
    //       value: 5,
    //       isSelected: false,
    //     },
    //   ],
    // },
  },
};

beforeEach(() => {
  wrapper = shallowMount(RatingShortcutsComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("RatingMonoSelectionComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(RatingShortcutsComponent)).toBe(true);
    expect(wrapper.vm.value).toBe("");
  });
  it.skip("change data value to 1 on press 1", () => {
    wrapper.trigger("keydown", { key: "1" });

    expect(wrapper.vm.value).toBe("1");
    document.getElementById = jest.fn();
  });
  it.skip("change data value to 12 on press 1 and then 2", () => {
    wrapper.trigger("keydown", { key: "1" });
    wrapper.trigger("keydown", { key: "2" });

    expect(wrapper.vm.value).toBe("12");
  });
  it.skip("click on target corresponding to value from shortcut", () => {});
});
