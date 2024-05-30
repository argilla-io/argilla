import { shallowMount } from "@vue/test-utils";
import SearchLabelComponent from "./SearchLabel.component";

let wrapper = null;
const options = {
  stubs: ["BaseIconWithBadge"],
  propsData: {
    searchRef: "searchRef",
    placeholder: "placeholder",
    value: "",
  },
};
const spyResetValueMethod = jest.spyOn(
  SearchLabelComponent.methods,
  "resetValue"
);

const spyFocusInSearchMethod = jest.spyOn(
  SearchLabelComponent.methods,
  "focusInSearch"
);

const spyLooseFocusMethod = jest.spyOn(
  SearchLabelComponent.methods,
  "looseFocus"
);

beforeEach(() => {
  wrapper = shallowMount(SearchLabelComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("LabelSelectionComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(SearchLabelComponent)).toBe(true);

    const textInput = wrapper.findComponent({ ref: "searchRef" });
    expect(textInput.exists()).toBe(true);

    expect(textInput.attributes("type")).toBe("text");
    expect(textInput.element.value).toBe("");
  });
  it("fill the text input with the props value and render a close button if value.length > 0", async () => {
    await wrapper.setProps({
      value: "the text written by the user",
    });
    await wrapper.vm.$nextTick();
    const closeButton = wrapper.findComponent({ ref: "iconCloseRef" });
    const textInput = wrapper.find('input[type="text"]');
    expect(closeButton.exists()).toBe(true);
    expect(textInput.element.value).toBe("the text written by the user");
  });
  it("emit when user write in the text input", async () => {
    const textInput = wrapper.find('input[type="text"]');
    await textInput.setValue("some value");

    expect(wrapper.find('input[type="text"]').element.value).toBe("some value");

    expect(wrapper.emitted("input")[0]).toStrictEqual(["some value"]);
  });
  it("focus on input text when user click on icon", async () => {
    const BaseSearchIconWithBadgeWrapper = wrapper.findComponent({
      ref: "iconSearchRef",
    });
    const textInput = wrapper.find('input[type="text"]');

    expect(BaseSearchIconWithBadgeWrapper.exists()).toBe(true);
    expect(textInput.exists()).toBe(true);
    await BaseSearchIconWithBadgeWrapper.trigger("click");

    await wrapper.vm.$nextTick();

    expect(spyFocusInSearchMethod).toHaveBeenCalled();
  });
  it("not reset the value when user click on BaseIcon component and there was no value in the input", async () => {
    const BaseSearchIconWithBadgeWrapper = wrapper.findComponent({
      ref: "iconCloseRef",
    });
    const textInput = wrapper.find('input[type="text"]');
    expect(BaseSearchIconWithBadgeWrapper.exists()).toBe(false);
    expect(textInput.exists()).toBe(true);
    expect(textInput.element.value).toBe("");
    await wrapper.vm.$nextTick();
    expect(wrapper.emitted("input")).toBeFalsy();
  });
  it("reset the value when user click on BaseIcon component and there is value in the input", async () => {
    await wrapper.setProps({
      value: "the text written by the user",
    });
    const BaseCloseIconWithBadgeWrapper = wrapper.findComponent({
      ref: "iconCloseRef",
    });
    await BaseCloseIconWithBadgeWrapper.vm.$emit("click-icon");
    await wrapper.vm.$nextTick();
    const textInput = wrapper.find('input[type="text"]');

    expect(BaseCloseIconWithBadgeWrapper.exists()).toBe(true);
    expect(textInput.exists()).toBe(true);

    expect(spyResetValueMethod).toHaveBeenCalled();
    expect(wrapper.emitted("input")[0]).toStrictEqual([""]);
  });
  it.skip("loose focus on input on shift+backspace shortcut", async () => {
    // FIXME - test input shortcut to loosefocus

    const textInput = wrapper.find('input[type="text"]');
    await textInput.trigger("keydown.shift.backspace.exact");

    await wrapper.vm.$nextTick();
    expect(spyLooseFocusMethod).toHaveBeenCalled();
  });
});
