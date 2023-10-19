import { shallowMount } from "@vue/test-utils";
import TextFieldComponent from "./TextField.component";

let wrapper = null;
const options = {
  stubs: ["BaseActionTooltip", "BaseButton", "RenderMarkdownBaseComponent"],
  propsData: {
    title: "Field title",
    fieldText: "# fieldText",
    useMarkdown: true,
  },
};

beforeEach(() => {
  wrapper = shallowMount(TextFieldComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("TaskSearchComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(TextFieldComponent)).toBe(true);
  });
  it("render markdown when useMarkdown is true", () => {
    expect(
      wrapper.findComponent({ name: "RenderMarkdownBaseComponent" }).exists()
    ).toBe(true);
  });
  it("prevent render markdown when useMarkdown is false", async () => {
    await wrapper.setProps({ useMarkdown: false });
    await wrapper.vm.$nextTick();
    expect(
      wrapper.findComponent({ name: "RenderMarkdownBaseComponent" }).exists()
    ).toBe(false);
  });
});
