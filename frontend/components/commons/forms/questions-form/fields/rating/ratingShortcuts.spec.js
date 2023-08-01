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

const spyOnIsValidKeyFor = jest.spyOn(
  RatingShortcutsComponent.methods,
  "isValidKeyFor"
);

beforeEach(() => {
  wrapper = shallowMount(RatingShortcutsComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("RatingMonoSelectionComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(RatingShortcutsComponent)).toBe(true);
  });
  it("validate shortcut when pressing numpad number", () => {
    for (let i = 1; i <= 10; i++) {
      const code = `Numpad${i}`;
      expect(spyOnIsValidKeyFor({ code })).toBe(true);
    }
  });
  it("validate shortcut when pressing digit number", () => {
    for (let i = 1; i <= 10; i++) {
      const code = `Digit${i}`;
      expect(spyOnIsValidKeyFor({ code })).toBe(true);
    }
  });
  it("not validate shortcut when not pressing a number", () => {
    const code = `KeyQ`;
    expect(spyOnIsValidKeyFor({ code })).toBe(false);
  });
  it.skip("click on target corresponding to value from shortcut", () => {
    wrapper.trigger("keydown", { key: "1" });
  });
});
