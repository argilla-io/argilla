import { shallowMount } from "@vue/test-utils";
import ComponentTextClassifierHelpInfo from "@/components/text-classifier/header/TextClassificationHelpInfo";

const props = {
  visible: true,
};

let wrapper = null;
beforeEach(() => {
  wrapper = shallowMount(ComponentTextClassifierHelpInfo, {
    stubs: ["lazy-base-modal", "base-button"],
    propsData: props,
  });
});
afterEach(() => {
  wrapper.destroy();
});
describe("TextClassificationHelpInfo", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    expect(wrapper).toMatchSnapshot();
  });
});
