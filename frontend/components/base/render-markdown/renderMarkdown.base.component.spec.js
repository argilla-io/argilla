import { mount } from "@vue/test-utils";
import RenderMarkdownBaseComponent from "./RenderMarkdown.base.component";

let wrapper = null;
const options = {
  components: { RenderMarkdownBaseComponent },
  propsData: {
    markdown: "# example",
  },
};

beforeEach(() => {
  wrapper = mount(RenderMarkdownBaseComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("RenderMarkdownBaseComponent", () => {
  it("render component", () => {
    expect(wrapper.is(RenderMarkdownBaseComponent)).toBe(true);
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
