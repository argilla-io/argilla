import { mount } from "@vue/test-utils";
import SelectOptions from "@/components/commons/header/filters/SelectOptions";

function mountSelectOptions() {
  return mount(SelectOptions, {
    stubs: ["base-checkbox"],
    propsData: {
      options: ["NEGATIVE", "POSITIVE", "OTHER"],
    },
  });
}

describe("SelectOptions", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountSelectOptions();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
