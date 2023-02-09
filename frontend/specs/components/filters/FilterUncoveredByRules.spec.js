import { mount } from "@vue/test-utils";
import FilterUncoveredByRules from "@/components/commons/header/filters/FilterUncoveredByRules";

function mountFilterUncoveredByRules() {
  return mount(FilterUncoveredByRules, {
    stubs: ["base-checkbox"],
    propsData: {
      dataset: {
        task: "TextClassification",
        rules: ["alta", "baja"],
      },
      filter: {
        selected: true,
      },
    },
  });
}

describe("FilterUncoveredByRules", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountFilterUncoveredByRules();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
