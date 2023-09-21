import { shallowMount } from "@vue/test-utils";
import BaseDropdown from "./BaseDropdown";

let wrapper = null;
const options = {
  propsData: {
    visible: false,
  },
};
beforeEach(() => {
  wrapper = shallowMount(BaseDropdown, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("BaseDropdownComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(BaseDropdown)).toBe(true);
  });
  it("expect to show dropdown on click dropdown header", async () => {
    testIfVisibleOnClickOnDropdown(true);
  });
  it("expect to close dropdown on click dropdown header", async () => {
    await wrapper.setProps({ visible: true });
    testIfVisibleOnClickOnDropdown(false);
  });
});

const testIfVisibleOnClickOnDropdown = async (value) => {
  const dropdownHeader = wrapper.find(".dropdown__header");
  dropdownHeader.trigger("click");
  wrapper.vm.$nextTick();
  expect(wrapper.emitted().visibility[0]).toEqual([value]);
};
