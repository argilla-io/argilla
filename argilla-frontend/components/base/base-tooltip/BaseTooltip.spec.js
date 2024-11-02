import { shallowMount } from "@vue/test-utils";
import BaseTooltip from "./BaseTooltip";

let wrapper = null;
const options = {
  propsData: {
    text: "this is a  tooltip message",
    position: "",
  },
};
beforeEach(() => {
  wrapper = shallowMount(BaseTooltip, options);
});

afterEach(() => {
  wrapper.destroy();
});
describe("BaseTooltip", () => {
  it("render the component", () => {
    expect(wrapper.is(BaseTooltip)).toBe(true);
    expect(wrapper.classes()).toContain("tooltip");
  });
  it("render the tooltip text", () => {
    expect(wrapper.text()).toBe("this is a  tooltip message");
  });
  it("on mouse enter show the tooltip", async () => {
    const tooltipTrigger = wrapper.findComponent({ ref: "tooltipWrapper" });
    await tooltipTrigger.trigger("mouseenter");
    const tooltipContent = wrapper.find(".tooltip-content");
    expect(tooltipContent.classes()).toContain("tooltip-content--show");
  });
  it("on mouse leave hide the tooltip", async () => {
    const tooltipTrigger = wrapper.findComponent({ ref: "tooltipWrapper" });
    await tooltipTrigger.trigger("mouseleave");
    const tooltipContent = wrapper.find(".tooltip-content");
    expect(tooltipContent.classes()).toContain("tooltip-content--hide");
  });
});
