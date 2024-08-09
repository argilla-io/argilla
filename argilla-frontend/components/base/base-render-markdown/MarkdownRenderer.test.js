import { shallowMount } from "@vue/test-utils";
import MarkdownRenderer from "./MarkdownRenderer";

const options = {
  components: { MarkdownRenderer },
  propsData: {
    markdown: "# example<script><TABLE> \n\n",
  },
  directives: {
    "copy-code"() {
      // copy code directive related to copy button
    },
  },
};

describe("MarkdownRenderer", () => {
  it("prevent render not allowed tags", async () => {
    const wrapper = shallowMount(MarkdownRenderer, options);
    expect(wrapper.html().includes("<script>")).toBe(false);
  });
  it("prevent render unsanitized html", async () => {
    const wrapper = shallowMount(MarkdownRenderer, options);
    expect(wrapper.html().includes("<TABLE>")).toBe(false);
  });
  it("render correct html", () => {
    const wrapper = shallowMount(MarkdownRenderer, options);
    expect(wrapper.html()).toBe(
      `<div class="markdown-render --ltr">
  <h1>example</h1>
</div>`
    );
  });
  it("add viewBox for svg", () => {
    const wrapper = shallowMount(MarkdownRenderer, {
      ...options,
      propsData: {
        markdown:
          '<svg height="100" width="100"><circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" /></svg>',
      },
    });
    expect(wrapper.html()).toBe(
      `<div class="markdown-render --ltr">
  <p><svg viewBox="0 0 100 100" width="100" height="100">
      <circle fill="red" stroke-width="3" stroke="black" r="40" cy="50" cx="50"></circle>
    </svg></p>
</div>`
    );
  });
  it("not add viewBox for svg if it has defined a viewport", () => {
    const wrapper = shallowMount(MarkdownRenderer, {
      ...options,
      propsData: {
        markdown:
          '<svg height="100" width="100" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" /></svg>',
      },
    });
    expect(wrapper.html()).toBe(
      `<div class="markdown-render --ltr">
  <p><svg viewBox="0 0 100 100" width="100" height="100">
      <circle fill="red" stroke-width="3" stroke="black" r="40" cy="50" cx="50"></circle>
    </svg></p>
</div>`
    );
  });

  it("open in other window if the node is a link", () => {
    const wrapper = shallowMount(MarkdownRenderer, {
      ...options,
      propsData: {
        markdown: "[example](https://example.com)",
      },
    });
    expect(wrapper.html()).toBe(
      `<div class="markdown-render --ltr">
  <p><a target="_blank" href="https://example.com">example</a></p>
</div>`
    );
  });

  it("open in other window if the node already hace target blank", () => {
    const wrapper = shallowMount(MarkdownRenderer, {
      ...options,
      propsData: {
        markdown: '<a href="https://example.com" target="_blank">example</a>',
      },
    });
    expect(wrapper.html()).toBe(
      `<div class="markdown-render --ltr">
  <p><a target="_blank" href="https://example.com">example</a></p>
</div>`
    );
  });
});
