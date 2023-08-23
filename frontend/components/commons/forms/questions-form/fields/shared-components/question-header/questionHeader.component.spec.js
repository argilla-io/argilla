import { shallowMount } from "@vue/test-utils";
import QuestionHeaderComponent from "./QuestionHeader.component";

let wrapper = null;
const options = {
  stubs: ["BaseIconWithBadge"],
  directives: {
    "required-field"() {
      // this directive is used to show a red asterisk at the end of a required question
    },
    tooltip() {
      // this directive is used to show a tooltip
    },
    "prefix-star"() {
      // this directive is used to show a spark icon
    },
  },
  propsData: {
    title: "This is a question to ask",
  },
};

beforeEach(() => {
  wrapper = shallowMount(QuestionHeaderComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("QuestionHeaderComponent", () => {
  it("render by default only the title of the question", () => {
    expect(wrapper.is(QuestionHeaderComponent)).toBe(true);

    expect(wrapper.vm.tooltipMessage).toBe("");

    expect(wrapper.vm.showIcon).toBe(false);

    expect(wrapper.find("span").exists()).toBe(true);
    expect(wrapper.find("span").text()).toBe("This is a question to ask");
    expect(wrapper.findComponent({ name: "BaseIconWithBadge" }).exists()).toBe(
      false
    );
  });
  it("render the BaseIconWithBadge component if there is a tooltipMessage", async () => {
    await wrapper.setProps({ tooltipMessage: "The tooltip message to show" });

    expect(wrapper.vm.showIcon).toBe(true);
    expect(wrapper.findComponent({ name: "BaseIconWithBadge" }).exists()).toBe(
      true
    );
  });
});
