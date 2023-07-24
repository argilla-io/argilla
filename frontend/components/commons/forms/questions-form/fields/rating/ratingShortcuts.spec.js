import { shallowMount } from "@vue/test-utils";
import RatingShortcutsComponent from "./RatingShortcuts";

let wrapper = null;
const options = {
  scopedSlots: {
    default: function (props) {
      return this.$createElement("div", [props.myProp]);
    },
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
  it("change data value to 1 on press 1", () => {
    wrapper.trigger("keydown", { key: "1" });

    expect(wrapper.vm.value).toBe("1");
    document.getElementById = jest.fn();
  });
  it("change data value to 12 on press 1 and then 2", () => {
    wrapper.trigger("keydown", { key: "1" });
    wrapper.trigger("keydown", { key: "2" });

    expect(wrapper.vm.value).toBe("12");
  });
  it.skip("click on target corresponding to value from shortcut", () => {});
});
