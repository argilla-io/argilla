import { mock } from "@codescouts/test/jest";
import { IFieldRepository } from "../services/IFieldRepository";
import { GetDatasetFieldsGroupedUseCase } from "./get-dataset-fields-grouped-use-case";

const createBackendField = (type: string) => {
  return {
    id: "1",
    name: "name",
    title: "title",
    required: true,
    settings: {
      type,
    },
  };
};

describe("GetDatasetFieldsGroupedUseCase should", () => {
  test("return a list of fields grouped by type", async () => {
    const datasetId = "datasetId";
    const backendFields = [
      createBackendField("chat"),
      createBackendField("chat"),
      createBackendField("text"),
    ];

    const fieldRepository = mock<IFieldRepository>();
    fieldRepository.getFields.mockResolvedValue(backendFields);

    const getDatasetFieldsGroupedUseCase = new GetDatasetFieldsGroupedUseCase(
      fieldRepository
    );

    const result = await getDatasetFieldsGroupedUseCase.execute(datasetId);

    expect(result).toHaveLength(2);
  });

  test("return an empty list if there are no fields", async () => {
    const datasetId = "datasetId";
    const backendFields = [];

    const fieldRepository = mock<IFieldRepository>();
    fieldRepository.getFields.mockResolvedValue(backendFields);

    const getDatasetFieldsGroupedUseCase = new GetDatasetFieldsGroupedUseCase(
      fieldRepository
    );

    const result = await getDatasetFieldsGroupedUseCase.execute(datasetId);

    expect(result).toHaveLength(0);
  });
});
