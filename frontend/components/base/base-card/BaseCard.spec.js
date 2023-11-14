import { shallowMount } from "@vue/test-utils";
import BaseCard from "./BaseCard";

let wrapper = null;
const options = {
  stubs: ["base-button"],
  propsData: {
    title: "title",
    subtitle: "subtitle",
    text: "text",
    buttonText: "delete",
    cardType: "danger",
  },
};
beforeEach(() => {
  wrapper = shallowMount(BaseCard, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("BaseCardComponent", () => {
  it("render the component", () => {
    expect(wrapper.is(BaseCard)).toBe(true);
  });
  it("expect title class to render", () => {
    isClassExist(".card__title");
  });
  it("expect subtitle class to render", () => {
    isClassExist(".card__subtitle");
  });
  it("expect text class to render", () => {
    isClassExist(".card__text");
  });
  it("expect button class to render", () => {
    isClassExist(".card__button");
  });
  it.skip("emit event when button is clicked", async () => {
    //FIXME - the expect is not complete since there is not the expecting value
    const button = wrapper.find(".card__button");
    button.trigger("click");
    wrapper.vm.$nextTick();
    expect(wrapper.emitted("card-action"));
  });
});

const isClassExist = async (className) => {
  expect(wrapper.find(className).exists()).toBe(true);
};
