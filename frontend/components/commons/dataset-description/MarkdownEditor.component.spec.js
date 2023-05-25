import { mount, shallowMount } from "@vue/test-utils";
import MarkdownEditorComponent from "./MarkdownEditor.component";
import MarkdownElementComponent from "./MarkdownElement.component";
import BaseButton from "@/components/base/BaseButton";

const placeholder = 'Test placeholder'
const defaultOptions = {
  components: { BaseButton, MarkdownElementComponent },
  propsData: {
    placeholder,
    value: ''
  }
}

describe('MarkdownEditorComponent', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(MarkdownEditorComponent, defaultOptions)

    expect(wrapper.is(MarkdownEditorComponent)).toBe(true)
  });

  it("shows a textarea input", () => {
    const wrapper = shallowMount(MarkdownEditorComponent, defaultOptions)

    const textarea = wrapper.find('textarea')

    expect(textarea.exists()).toBe(true)
  })

  it("shows a markdown preview", () => {
    const wrapper = shallowMount(MarkdownEditorComponent, defaultOptions)

    const textarea = wrapper.find('markdownelementcomponent-stub')

    expect(textarea.exists()).toBe(true)
  })

  it('shows a placeholder when no text is provided', () => {
    const wrapper = shallowMount(MarkdownEditorComponent, defaultOptions)
    const textarea = wrapper.find('textarea')

    expect(textarea.attributes('placeholder')).toBe(placeholder)
  });

  it('shows the existing markdown when is provided', () => {
    const text = 'this is a markdown'

    const options = {
      components: { BaseButton, MarkdownElementComponent },
      propsData: {
        placeholder: '',
        value: text
      }
    }
    const wrapper = shallowMount(MarkdownEditorComponent, options)
    const textarea = wrapper.find('textarea')

    expect(textarea.element.value).toBe(text)
  });

  it('sends a save event when the save button is clicked', async () => {
    const wrapper = mount(MarkdownEditorComponent, defaultOptions)

    const button = wrapper.find('button')
    await button.trigger("click")

    expect(wrapper.emitted()).toHaveProperty('save')
  })

});
