import { mount } from "@vue/test-utils";
import ComponentTextClassifierViewInfo from "@/components/text-classifier/sidebar/TextClassificationViewInfo";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";

const props = {
  dataset: {
    task: "TextClassification",
    viewSettings: new DatasetViewSettings({
      visibleViewInfo: true,
    }),
  },
};

let wrapper = null;
beforeEach(() => {
  wrapper = mount(ComponentTextClassifierViewInfo, {
    propsData: props,
  });
});
afterEach(() => {
  wrapper.destroy();
});
describe("TextClassificationViewInfo", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("Required property", () => {
    expect(ComponentTextClassifierViewInfo.props.dataset.required).toBe(true);
  });

  test("renders properly", () => {
    expect(wrapper).toMatchSnapshot();
  });
});
