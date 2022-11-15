import { shallowMount } from "@vue/test-utils";
import ComponentTextClassifierHelpInfo from "@/components/text-classifier/header/TextClassificationhelpInfo";

const props = {
  visible: true,
};

let wrapper = null;
beforeEach(() => {
  wrapper = shallowMount(ComponentTextClassifierHelpInfo, {
    propsData: props,
  });
});
afterEach(() => {
  wrapper.destroy();
});
describe("TextClassificationhelpInfo", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("Required property", () => {
    expect(ComponentTextClassifierHelpInfo.props.visible.required).toBe(true);
  });

  test("renders properly", () => {
    expect(wrapper).toMatchSnapshot();
  });
});
