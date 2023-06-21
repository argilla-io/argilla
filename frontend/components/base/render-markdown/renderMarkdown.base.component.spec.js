import { shallowMount } from "@vue/test-utils";
import RenderMarkdownBaseComponent from "./RenderMarkdown.base.component";

let wrapper = null;
const options = {
  components: { RenderMarkdownBaseComponent },
  propsData: {
    markdown: "# example<script><TABLE> \n\n",
  },
};

const spyCleanMarkdownMethod = jest.spyOn(
  RenderMarkdownBaseComponent.methods,
  "cleanMarkdown"
);

beforeEach(() => {
  wrapper = shallowMount(RenderMarkdownBaseComponent, options);
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
    expect(wrapper.html().includes("<script>")).toBe(false);
  });

  it("prevent render unsanitized html", async () => {
    expect(wrapper.html().includes("<TABLE>")).toBe(false);
  });
  it("expect cleanMarkdown method to been called", async () => {
    expect(spyCleanMarkdownMethod).toHaveBeenCalled();
  });
  it("clean trailing spaces in markdown", async () => {
    const cleanedMarkdownText = await spyCleanMarkdownMethod(
      wrapper.props().markdown
    );
    await wrapper.vm.$nextTick();
    expect(cleanedMarkdownText).toBe(`# example<script><TABLE>

`);
    expect(cleanedMarkdownText).not.toBe(`# example<script><TABLE>`);
  });
  it("render correct html", () => {
    expect(wrapper.html()).toBe(
      `<div class="markdown-render">
  <h1>example</h1>
</div>`
    );
  });
});
