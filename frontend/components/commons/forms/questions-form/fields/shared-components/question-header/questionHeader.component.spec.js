import { shallowMount } from "@vue/test-utils";
import QuestionHeaderComponent from "./QuestionHeader.component";

let wrapper = null;
const options = {
  stubs: ["BaseIconWithBadge"],
  directives: {
    "optional-field"() {
      // this directive is used to show '(optional)' at the end of a question optional
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
  it.skip("render the optional-field directive if the question is not required", async () => {
    await wrapper.setProps({ isRequired: true });
    const getAllByText = (wrapper, text) => {
      //  Get all elements with the given text.
      return wrapper.findAll("*").filter((node) => node.text() === text);
    };

    const getByText = (wrapper, text) => {
      // Get the first element that has the given text.

      const results = getAllByText(wrapper, text);
      if (results.length === 0) {
        throw new Error(
          `getByText() found no element with the text: "${text}".`
        );
      }
      return results.at(0);
    };

    // FIXME - test that the question text have ' (optional)' at the end
    // console.log(wrapper.find("span").element.innerHTML);

    // expect(wrapper.find(" (optional)")" (optional)".exists()).toBe(true);
    // expect(wrapper.vm.showAsOptional).toBe(false); // by default question is optional

    expect(getByText(wrapper, "This is a question to ask").exists()).toBe(true);
    // console.log(getByText(wrapper, " (optional)"));
  });
  it("render the BaseIconWithBadge component if there is a tooltipMessage", async () => {
    await wrapper.setProps({ tooltipMessage: "The tooltip message to show" });

    expect(wrapper.vm.showIcon).toBe(true);
    expect(wrapper.findComponent({ name: "BaseIconWithBadge" }).exists()).toBe(
      true
    );
  });
});
