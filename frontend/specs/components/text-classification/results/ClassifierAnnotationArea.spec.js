import { mount } from "@vue/test-utils";
import Component from "@/components/text-classifier/results/ClassifierAnnotationArea";

import { TextClassificationRecord } from "@/models/TextClassification";

const $route = {
  query: {},
};

function mountSidebar() {
  return mount(Component, {
    propsData: {
      record: new TextClassificationRecord({
        inputs: { text: "My text", multi_label: false },
      }),
      dataset: {
        task: "TextClassification",
        viewSettings: {
          annotationEnabled: false,
        },
        labels: ["A", "B"],
      },
    },
    mocks: {
      $route,
    },
  });
}

describe("ClassifierAnnotationArea", () => {
  let spy = jest.spyOn(console, "error");
  afterEach(() => spy.mockReset());

  test("Required property", () => {
    expect(() => {
      mount(Component);
      expect(spy).toBeCalledWith(
        expect.stringContaining('[Vue warn]: Missing required prop: "dataset"')
      );
    }).toThrowError(TypeError);
  });

  test("renders properly", () => {
    const wrapper = mountSidebar();
    expect(wrapper).toMatchSnapshot();
  });
});
