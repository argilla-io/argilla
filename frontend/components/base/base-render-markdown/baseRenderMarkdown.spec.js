import { mount } from "@vue/test-utils";
import BaseRenderMarkdown from "./BaseRenderMarkdown";

let wrapper = null;
const options = {
  components: { BaseRenderMarkdown },
  propsData: {
    markdown: "# example",
  },
};

beforeEach(() => {
  wrapper = mount(BaseRenderMarkdown, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("BaseRenderMarkdown", () => {
  it("render component", () => {
    expect(wrapper.is(BaseRenderMarkdown)).toBe(true);
  });

  it("render parsed html", () => {
    expect(wrapper.html().includes("h1")).toBe(true);
  });

  it("prevent render not allowed tags", async () => {
    await wrapper.setProps({ markdown: "<script>" });
    await wrapper.vm.$nextTick();
    expect(wrapper.html().includes("<script>")).toBe(false);
  });

  it("prevent render unsanitized html", async () => {
    await wrapper.setProps({ markdown: "<TABLE>" });
    await wrapper.vm.$nextTick();
    expect(wrapper.html().includes("<TABLE>")).toBe(false);
  });
});
