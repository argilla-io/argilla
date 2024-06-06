import { mock } from "@codescouts/test/jest";
import { IQuestionRepository } from "../services/IQuestionRepository";
import { GetDatasetQuestionsGroupedUseCase } from "./get-dataset-questions-grouped-use-case";

const createBackendQuestion = (type: string) => {
  return {
    id: "1",
    name: "name",
    description: "description",
    title: "title",
    required: true,
    settings: {
      type,
      options: [
        {
          description: "description",
          text: "text",
          value: "value",
        },
      ],
    },
  };
};

describe("GetDatasetQuestionsGroupedUseCase should", () => {
  test("return a list of questions grouped by type", async () => {
    const datasetId = "datasetId";
    const backendQuestions = [
      createBackendQuestion("label_selection"),
      createBackendQuestion("label_selection"),
      createBackendQuestion("rating"),
    ];

    const questionRepository = mock<IQuestionRepository>();
    questionRepository.getQuestions.mockResolvedValue(backendQuestions);

    const getDatasetQuestionsGroupedUseCase =
      new GetDatasetQuestionsGroupedUseCase(questionRepository);

    const result = await getDatasetQuestionsGroupedUseCase.execute(datasetId);

    expect(result).toHaveLength(2);
  });

  test("return an empty list if there are no questions", async () => {
    const datasetId = "datasetId";
    const backendQuestions = [];

    const questionRepository = mock<IQuestionRepository>();
    questionRepository.getQuestions.mockResolvedValue(backendQuestions);

    const getDatasetQuestionsGroupedUseCase =
      new GetDatasetQuestionsGroupedUseCase(questionRepository);

    const result = await getDatasetQuestionsGroupedUseCase.execute(datasetId);

    expect(result).toHaveLength(0);
  });
});
