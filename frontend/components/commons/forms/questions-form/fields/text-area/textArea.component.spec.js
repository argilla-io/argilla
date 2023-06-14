import { shallowMount } from "@vue/test-utils";
import TextAreaComponent from "./TextArea.component";

let wrapper = null;
const options = {
  stubs: [
    "QuestionHeaderComponent",
    "RenderMarkdownBaseComponent",
    "ContentEditableFeedbackTask",
  ],
  propsData: {
    title: "This is the title",
  },
};

const spyOnChangeTextArea = jest.spyOn(
  TextAreaComponent.methods,
  "onChangeTextArea"
);

beforeEach(() => {
  wrapper = shallowMount(TextAreaComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("TextAreaComponent", () => {
  it("render the component as a content editable by default", () => {
    expect(wrapper.is(TextAreaComponent)).toBe(true);

    expect(wrapper.vm.value).toBe("");
    expect(wrapper.vm.placeholder).toBe("");
    expect(wrapper.vm.isRequired).toBe(false);
    expect(wrapper.vm.description).toBe("");
    expect(wrapper.vm.useMarkdown).toBe(false);
    expect(wrapper.vm.isFocused).toBe(false);

    const QuestionHeaderWrapper = wrapper.findComponent({
      name: "QuestionHeaderComponent",
    });
    expect(QuestionHeaderWrapper.exists()).toBe(true);

    const containerWrapper = wrapper.find(".container");
    expect(containerWrapper.exists()).toBe(true);

    const BaseRenderMarkdownWrapper = wrapper.findComponent({
      name: "RenderMarkdownBaseComponent",
    });
    expect(BaseRenderMarkdownWrapper.exists()).toBe(false);

    const ContentEditableFeedbackTaskWrapper = wrapper.findComponent({
      name: "ContentEditableFeedbackTask",
    });
    expect(ContentEditableFeedbackTaskWrapper.exists()).toBe(true);
  });
  it("emit event to the parent the new value received by the ContentEditableFeedbackTask component", async () => {
    const ContentEditableFeedbackTaskWrapper = wrapper.findComponent({
      name: "ContentEditableFeedbackTask",
    });
    expect(ContentEditableFeedbackTaskWrapper.exists()).toBe(true);
    await ContentEditableFeedbackTaskWrapper.vm.$emit(
      "change-text",
      "This is an updated text"
    );
    await wrapper.vm.$nextTick();

    expect(spyOnChangeTextArea).toHaveBeenCalled();
    expect(wrapper.emitted("on-change-value")[0]).toEqual([
      "This is an updated text",
    ]);
  });
  it("render the markdown component if the corresponding flag is true", async () => {
    await wrapper.setProps({
      useMarkdown: true,
      value: "This is the content of the text",
    });

    expect(wrapper.vm.useMarkdown).toBe(true);
    expect(wrapper.vm.value).toBe("This is the content of the text");

    const QuestionHeaderWrapper = wrapper.findComponent({
      name: "QuestionHeaderComponent",
    });
    expect(QuestionHeaderWrapper.exists()).toBe(true);

    const BaseRenderMarkdownWrapper = wrapper.findComponent({
      name: "RenderMarkdownBaseComponent",
    });
    expect(BaseRenderMarkdownWrapper.exists()).toBe(true);

    const ContentEditableFeedbackTaskWrapper = wrapper.findComponent({
      name: "ContentEditableFeedbackTask",
    });
    expect(ContentEditableFeedbackTaskWrapper.exists()).toBe(false);
  });
});
