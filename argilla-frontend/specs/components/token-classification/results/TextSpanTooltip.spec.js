import { mount } from "@vue/test-utils";
import TextSpanTooltipVue from "@/components/token-classification/results/TextSpanTooltip.vue";

function mountTextSpanTooltip() {
  return mount(TextSpanTooltipVue, {
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
  const spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("renders properly", () => {
    const wrapper = mountTextSpanTooltip();
    expect(wrapper.html()).toMatchSnapshot();
  });
});
