import { shallowMount } from "@vue/test-utils";
import TextClassificationBulkAnnotationComponent from "./TextClassificationBulkAnnotation.component";

let wrapper = null;
const options = {
  stubs: ["BulkAnnotationComponent"],
  propsData: {
    datasetId: ["owner", "name"],
    labels: [
      "Alcantarillado/Pluviales",
      "Alta",
      "Aplazamiento de pago",
      "Atención recibida",
    ],
    recordsIds: new Set(["b5a23810-10e9-4bff-adf3-447a45667299"]),
    records: [
      {
        id: "b5a23810-10e9-4bff-adf3-447a45667299",
        metadata: {},
        annotation: {
          agent: "recognai",
          labels: [
            {
              class: "Alcantarillado/Pluviales",
              score: 1,
            },
            {
              class: "Atención recibida",
              score: 1,
            },
          ],
        },
        status: "Validated",
        selected: true,
        vectors: {},
        last_updated: "2023-02-04T02:07:34.965243",
        search_keywords: [],
        inputs: {
          text: "Esto es un registro sin predicciones ni anotaciones",
        },
        multi_label: true,
        currentAnnotation: {
          agent: "recognai",
          labels: [
            {
              class: "Alcantarillado/Pluviales",
              score: 1,
            },
            {
              class: "Atención recibida",
              score: 1,
            },
          ],
        },
      },
    ],
  },
};

const spyUpdateAnnotations = jest.spyOn(
  TextClassificationBulkAnnotationComponent.methods,
  "updateAnnotations"
);
beforeEach(() => {
  wrapper = shallowMount(TextClassificationBulkAnnotationComponent, options);
});

afterEach(() => {
  wrapper.destroy();
});

describe("TextClassificationBulkAnnotationComponent", () => {
  it("render the component", () => {
    expect(true).toBe(true);
  });
  it("format the labels for the bulk annotation formular", () => {
    expect(wrapper.vm.formattedLabelsForBulkAnnotationForm).toStrictEqual([
      {
        record_ids: new Set().add("b5a23810-10e9-4bff-adf3-447a45667299"),
        id: "Alcantarillado/Pluviales",
        label: "Alcantarillado/Pluviales",
        selected: true,
        removed: false,
        unmodified: false,
      },
      {
        record_ids: new Set(),
        id: "Alta",
        label: "Alta",
        selected: false,
        removed: false,
        unmodified: false,
      },
      {
        record_ids: new Set(),
        id: "Aplazamiento de pago",
        label: "Aplazamiento de pago",
        selected: false,
        removed: false,
        unmodified: false,
      },
      {
        record_ids: new Set().add("b5a23810-10e9-4bff-adf3-447a45667299"),
        id: "Atención recibida",
        label: "Atención recibida",
        selected: true,
        removed: false,
        unmodified: false,
      },
    ]);
  });

  it("emit the updated annotations from the BulkAnnotation component", () => {
    const BulkAnnotationWrapper = wrapper.find(".bulk-annotation-component");
    expect(BulkAnnotationWrapper.exists()).toBe(true);

    const emittedAnnotations = [
      {
        record_ids: new Set().add("b5a23810-10e9-4bff-adf3-447a45667299"),
        id: "Alcantarillado/Pluviales",
        label: "Alcantarillado/Pluviales",
        selected: true,
        removed: false,
        unmodified: false,
      },
      {
        record_ids: new Set(),
        id: "Alta",
        label: "Alta",
        selected: false,
        removed: false,
        unmodified: false,
      },
      {
        record_ids: new Set(),
        id: "Aplazamiento de pago",
        label: "Aplazamiento de pago",
        selected: false,
        removed: false,
        unmodified: false,
      },
      {
        record_ids: new Set(),
        id: "Atención recibida",
        label: "Atención recibida",
        selected: false,
        removed: false,
        unmodified: false,
      },
    ];

    BulkAnnotationWrapper.vm.$emit("on-update-annotations", emittedAnnotations);

    expect(spyUpdateAnnotations).toHaveBeenCalledWith(emittedAnnotations);

    expect(wrapper.emitted("on-update-annotations")[0]).toStrictEqual([
      emittedAnnotations,
    ]);
  });
});
