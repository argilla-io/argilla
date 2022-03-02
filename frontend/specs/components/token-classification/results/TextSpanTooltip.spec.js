import { mount } from "@vue/test-utils";
import TextSpanTooltip from "@/components/token-classifier/results/TextSpanTooltip";

function mountTextSpanTooltip() {
  return mount(TextSpanTooltip, {
    propsData: {
      span: {
        end: 73,
        entity: {
          end: 73,
          end_token: 15,
          label: "Arreglo",
          start: 57,
          start_token: 13,
        },
        origin: "annotation",
      },
    },
  });
}

describe("TextSpanTooltip", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountTextSpanTooltip();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
