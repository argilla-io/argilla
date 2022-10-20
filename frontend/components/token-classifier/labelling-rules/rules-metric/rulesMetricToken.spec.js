import { shallowMount } from "@vue/test-utils";
import RulesMetricToken from "./RulesMetricToken.component";

let wrapper = null;
const options = {
  propsData: {
    title: "Title of Rules Metric",
    subcardInputs: [
      {
        id: "subCard1",
        label: "coverage",
        mainValue: "5%",
        subValue: "5/100",
        tooltip: {
          tooltipMessage: "This is the tooltip message for subcard 1",
          tooltipDirection: "right",
        },
      },
      {
        id: "subCard2",
        label: "Annotated coverage",
        mainValue: "12%",
        subValue: "12/30",
        tooltip: {
          tooltipMessage: "This is the tooltip message for subcard 2",
          tooltipDirection: "left",
        },
      },
    ],
  },
};
beforeEach(() => {
  wrapper = shallowMount(RulesMetricToken, options);
});

afterEach(() => {
  wrapper.destroy();
});
describe("RulesMetricToken", () => {
  it("render the component", () => {
    expect(wrapper.is(RulesMetricToken)).toBe(true);
    expect(wrapper.find(".rule-metrics-token__title").text()).toContain(
      options.propsData.title
    );
    expect(wrapper.find(".subcard").exists()).toBe(true);
    expect(wrapper.find(".rule-metrics-token__bottom").exists()).toBe(false);
    expect(wrapper.findAll(".subcard").length).toBe(
      options.propsData.subcardInputs.length
    );
    //value by default
    expect(wrapper.vm.cssVars).toStrictEqual({
      "--number-of-rows": 1,
      "--number-of-columns": 2,
      "--text-color": "white",
      "--background-color": "#0508D9",
      "--background-subcard-color": "#0508D9",
    });
  });
  it("emit an event on click on the button (there is a button IF there is a btnLabel props)", async () => {
    await wrapper.setProps({ btnLabel: "Click me" });
    expect(wrapper.find(".rule-metrics-token__bottom").exists()).toBe(true);
    await wrapper.find("button").trigger("click");
    expect(wrapper.emitted()).toHaveProperty("onClickBottomBtn");
  });
});
