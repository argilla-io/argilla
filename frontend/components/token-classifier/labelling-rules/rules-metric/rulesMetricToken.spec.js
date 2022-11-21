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
    expect(wrapper.find(".rule-metrics__title").text()).toContain(
      options.propsData.title
    );
    expect(wrapper.find(".subcard").exists()).toBe(true);
    expect(wrapper.find(".rule-metrics__bottom").exists()).toBe(false);
    expect(wrapper.findAll(".subcard").length).toBe(
      options.propsData.subcardInputs.length
    );
    //value by default
    expect(wrapper.vm.cssVars).toStrictEqual({
      "--background-color": "#0508D9",
      "--border-color": "black",
      "--number-of-rows": 1,
      "--number-of-columns": 2,
      "--text-color": "white",
      "--text-subcard-color": "black",
    });
  });
});
