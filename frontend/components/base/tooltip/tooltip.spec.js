import { shallowMount } from "@vue/test-utils";
import TooltipComponent from "./Tooltip.component";

let wrapper = null;
const options = {
  propsData: {
    message: "this is a  tooltip message",
    direction: "",
  },
};
beforeEach(() => {
  wrapper = shallowMount(TooltipComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});
describe("TooltipComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(TooltipComponent)).toBe(true);
    expect(wrapper.classes()).toContain("tooltip-component");
    expect(wrapper.find("[data-title]").exists()).toBe(true);
  });
  it("not add tooltip if any direction is field", () => {
    expect(wrapper.vm.tooltipDirection).toBe("");
    expect(wrapper.find(".top").exists()).toBe(false);
    expect(wrapper.find(".right").exists()).toBe(false);
    expect(wrapper.find(".bottom").exists()).toBe(false);
    expect(wrapper.find(".left").exists()).toBe(false);
  });
  it("not add tooltip if direction props is 'none'", async () => {
    await wrapper.setProps({ direction: "none" });
    expect(wrapper.vm.tooltipDirection).toBe("");
    expect(wrapper.find(".top").exists()).toBe(false);
    expect(wrapper.find(".right").exists()).toBe(false);
    expect(wrapper.find(".bottom").exists()).toBe(false);
    expect(wrapper.find(".left").exists()).toBe(false);
  });
  it("add tooltip on top if direction props is 'top', (not case sensitive)", async () => {
    await wrapper.setProps({ direction: "tOp" });
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.tooltipDirection).toBe("top");
    expect(wrapper.find(".top").exists()).toBe(true);
    expect(wrapper.find(".right").exists()).toBe(false);
    expect(wrapper.find(".bottom").exists()).toBe(false);
    expect(wrapper.find(".left").exists()).toBe(false);
  });
  it("add tooltip on right if direction props is 'right', (not case sensitive)", async () => {
    await wrapper.setProps({ direction: "RiGhT" });
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.tooltipDirection).toBe("right");
    expect(wrapper.find(".top").exists()).toBe(false);
    expect(wrapper.find(".right").exists()).toBe(true);
    expect(wrapper.find(".bottom").exists()).toBe(false);
    expect(wrapper.find(".left").exists()).toBe(false);
  });
  it("add tooltip on bottom if direction props is 'bottom', (not case sensitive)", async () => {
    await wrapper.setProps({ direction: "bOTtOm" });
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.tooltipDirection).toBe("bottom");
    expect(wrapper.find(".top").exists()).toBe(false);
    expect(wrapper.find(".right").exists()).toBe(false);
    expect(wrapper.find(".bottom").exists()).toBe(true);
    expect(wrapper.find(".left").exists()).toBe(false);
  });
  it("add tooltip on left if direction props is 'left', (not case sensitive)", async () => {
    await wrapper.setProps({ direction: "LEfT" });
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.tooltipDirection).toBe("left");
    expect(wrapper.find(".top").exists()).toBe(false);
    expect(wrapper.find(".right").exists()).toBe(false);
    expect(wrapper.find(".bottom").exists()).toBe(false);
    expect(wrapper.find(".left").exists()).toBe(true);
  });
});
