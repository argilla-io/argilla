import { mount } from "@vue/test-utils";
import BaseSlider from "@/components/base/base-slider/BaseSlider";

function mountBaseSlider() {
  return mount(BaseSlider, {
    propsData: {
      slidesName: "sentences",
      slidesOrigin: ["first sentence", "second sentence"],
      itemNumber: 0,
    },
  });
}

describe("BaseSlider", () => {
  const spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountBaseSlider();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
