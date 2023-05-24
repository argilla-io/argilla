import { shallowMount } from "@vue/test-utils";
import MarkdownEditor from "./MarkdownEditor.component";

describe('MarkdownEditorComponent', () => {
  it('renders the component', () => {
    const options = {
      placeholder: 'Test placeholder',
      value: ''
    }
    const wrapper = shallowMount(MarkdownEditor, options)

    expect(wrapper.is(MarkdownEditor)).toBe(true)
  });

  it("shows a textarea input", () => {
    const options = {
      placeholder: 'Test placeholder',
      value: ''
    }
    const wrapper = shallowMount(MarkdownEditor, options)

    const textarea = wrapper.find('textarea')

    expect(textarea.exists()).toBe(true)
  })

  it("shows a markdown preview", () => {
    const options = {
      placeholder: 'Test placeholder',
      value: ''
    }
    const wrapper = shallowMount(MarkdownEditor, options)

    const textarea = wrapper.find('markdown-element-stub')

    expect(textarea.exists()).toBe(true)
  })

  it('shows a placeholder when no text is provided', () => {
    const placeholder = 'Test placeholder'

    const options = {
      propsData: {
        placeholder,
        value: ''
      }
    }
    const wrapper = shallowMount(MarkdownEditor, options)
    const textarea = wrapper.find('textarea')

    expect(textarea.attributes('placeholder')).toBe(placeholder)
  });

  it('shows the existing markdown when is provided', () => {
    const text = 'this is a markdown'

    const options = {
      propsData: {
        placeholder: '',
        value: text
      }
    }
    const wrapper = shallowMount(MarkdownEditor, options)
    const textarea = wrapper.find('textarea')

    expect(textarea.element.value).toBe(text)
  });

  it('sends a save event when the save button is clicked', async () => {
    const options = {
      propsData: {
        placeholder: '',
        value: ''
      }
    }

    const wrapper = shallowMount(MarkdownEditor, options)

    const button = wrapper.find('base-button')
    await button.trigger("click")

    expect(wrapper.emitted()).toHaveProperty('save')
  })

});
