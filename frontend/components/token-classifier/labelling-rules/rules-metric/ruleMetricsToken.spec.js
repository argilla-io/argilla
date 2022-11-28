import { shallowMount } from "@vue/test-utils";
import RuleMetricsToken from "./RuleMetricsToken.component";

let wrapper = null;
const options = {
  propsData: {
    title: "Title of Rule Metrics",
    ruleMetricsType: "info",
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
  wrapper = shallowMount(RuleMetricsToken, options);
});

afterEach(() => {
  wrapper.destroy();
});
describe("RulesMetricToken", () => {
  it("render the component", () => {
    expect(wrapper.is(RuleMetricsToken)).toBe(true);
    expect(wrapper.find(".rule-metrics-token__title").text()).toContain(
      options.propsData.title
    );
    expect(wrapper.find(".rule-metrics-token--info").exists()).toBe(true);
    expect(wrapper.find(".subcard").exists()).toBe(true);
    expect(wrapper.find(".rule-metrics__bottom").exists()).toBe(false);
    expect(wrapper.findAll(".subcard").length).toBe(
      options.propsData.subcardInputs.length
    );
    //value by default
    expect(wrapper.vm.cssVars).toStrictEqual({
      "--number-of-rows": 1,
      "--number-of-columns": 2,
    });
  });
});
