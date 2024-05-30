import { mount } from "@vue/test-utils";
import SelectOptions from "@/components/base/base-table/filters/SelectOptions.vue";

function mountSelectOptions() {
  return mount(SelectOptions, {
    stubs: ["base-checkbox"],
    propsData: {
      options: ["NEGATIVE", "POSITIVE", "OTHER"],
    },
  });
}

describe("SelectOptions", () => {
  const spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountSelectOptions();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
