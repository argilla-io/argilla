import { mount } from "@vue/test-utils";
import Component from "@/components/text-classifier/results/RecordTextClassification";

import { TextClassificationRecord } from "@/models/TextClassification";

const $route = {
  query: {},
};

function mountComponent() {
  return mount(Component, {
    propsData: {
      record: new TextClassificationRecord({
        inputs: {
          text: "My text",
          multi_label: true,
          prediction: {
            agent: "test",
            labels: [
              { class: "Test", score: 0.6 },
              { class: "A", score: 0.4 },
              { class: "B", score: 0.2 },
            ],
          },
        },
      }),
      dataset: {
        task: "TextClassification",
        query: {
          text: "mock test",
        },
        viewSettings: {
          annotationEnabled: false,
        },
        labels: ["Test", "A", "B"],
      },
    },
    mocks: {
      $route,
    },
  });
}

describe("RecordTextClassification", () => {
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
    const wrapper = mountComponent();
    expect(wrapper).toMatchSnapshot();
  });
});
