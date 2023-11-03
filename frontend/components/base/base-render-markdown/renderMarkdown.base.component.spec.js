import { shallowMount } from "@vue/test-utils";
import RenderMarkdownBaseComponent from "./RenderMarkdown.base.component";

const options = {
  components: { RenderMarkdownBaseComponent },
  propsData: {
    markdown: "# example<script><TABLE> \n\n",
  },
  directives: {
    "copy-code"() {
      // copy code directive related to copy button
    },
  },
};

describe("RenderMarkdownBaseComponent", () => {
  it("prevent render not allowed tags", async () => {
    const wrapper = shallowMount(RenderMarkdownBaseComponent, options);
    expect(wrapper.html().includes("<script>")).toBe(false);
  });
  it("prevent render unsanitized html", async () => {
    const wrapper = shallowMount(RenderMarkdownBaseComponent, options);
    expect(wrapper.html().includes("<TABLE>")).toBe(false);
  });
  it("render correct html", () => {
    const wrapper = shallowMount(RenderMarkdownBaseComponent, options);
    expect(wrapper.html()).toBe(
      `<div class="markdown-render">
  <h1>example</h1>
</div>`
    );
  });
  it("add viewBox for svg", () => {
    const wrapper = shallowMount(RenderMarkdownBaseComponent, {
      ...options,
      propsData: {
        markdown: `<svg height="100" width="100"><circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" /></svg>`,
      },
    });
    expect(wrapper.html()).toBe(
      `<div class="markdown-render">
  <p><svg viewBox="0 0 100 100" width="100" height="100">
      <circle fill="red" stroke-width="3" stroke="black" r="40" cy="50" cx="50"></circle>
    </svg></p>
</div>`
    );
  });
  it("not add viewBox for svg if it has defined a viewport", () => {
    const wrapper = shallowMount(RenderMarkdownBaseComponent, {
      ...options,
      propsData: {
        markdown: `<svg height="100" width="100" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" /></svg>`,
      },
    });
    expect(wrapper.html()).toBe(
      `<div class="markdown-render">
  <p><svg viewBox="0 0 100 100" width="100" height="100">
      <circle fill="red" stroke-width="3" stroke="black" r="40" cy="50" cx="50"></circle>
    </svg></p>
</div>`
    );
  });
});
