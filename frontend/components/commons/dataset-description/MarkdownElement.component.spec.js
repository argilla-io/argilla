import { shallowMount } from "@vue/test-utils";
import MarkdownElement from "./MarkdownElement.component";

let wrapper = null;
const options = {
  propsData: {
    markdown: '# title',
  },
};

beforeEach(() => {
  wrapper = shallowMount(MarkdownElement, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe('MarkdownElementComponent', () => {
  it('renders the component', () => {
    expect(wrapper.is(MarkdownElement)).toBe(true)
  });

  it('renders the markup as html', () => {
    expect(wrapper.html().includes('h1')).toBe(true)
  });

  it('prevents malicious code to be inserted', async () => {
    const maliciousCode = '<script></script>'
    await wrapper.setProps({markdown: maliciousCode})

    expect(wrapper.html().includes('script')).toBe(false)
  });
});
