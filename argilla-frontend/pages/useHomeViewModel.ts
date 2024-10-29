import { useResolve } from "ts-injecty";
import { ref, useFetch } from "@nuxtjs/composition-api";
import { useRoutes, useFocusTab } from "~/v1/infrastructure/services";
import { GetDatasetCreationUseCase } from "~/v1/domain/usecases/get-dataset-creation-use-case";
import { GetDatasetsUseCase } from "@/v1/domain/usecases/get-datasets-use-case";
import { useDatasets } from "~/v1/infrastructure/storage/DatasetsStorage";
import { useRole } from "~/v1/infrastructure/services/useRole";

export const useHomeViewModel = () => {
  const { isAdminOrOwnerRole } = useRole();
  const isLoadingDatasets = ref(false);
  const { goToImportDatasetFromHub } = useRoutes();
  const { state: datasets } = useDatasets();
  const getDatasetsUseCase = useResolve(GetDatasetsUseCase);
  const getDatasetCreationUseCase = useResolve(GetDatasetCreationUseCase);
  const error = ref("");

  useFocusTab(async () => {
    await onLoadDatasets();
  });

  useFetch(() => {
    loadDatasets();
  });

  const getNewDatasetByRepoId = async (repositoryId: string) => {
    try {
      await getDatasetCreationUseCase.execute(repositoryId);
      goToImportDatasetFromHub(repositoryId);
    } catch {
      error.value = "datasetCreation.cantLoadRepository";
    }
  };

  const exampleDatasets = [
    {
      repoId: "stanfordnlp/imdb",
      task: "Text Classification",
      tags: ["sentiment-classification"],
      icon: "text-classification",
      color: "hsl(25, 95%, 53%)",
      rows: "100K",
    },
    {
      repoId: "databricks/databricks-dolly-15k",
      task: "Question answering",
      tags: ["instruction-dataset", "rag"],
      icon: "question-answering",
      color: "hsl(217, 91%, 60%)",
      rows: "15K",
    },
    {
      repoId: "dvilasuero/finepersonas-v0.1-tiny-flux-schnell",
      task: "Text to Image",
      tags: ["synthetic", "rlaif"],
      icon: "text-to-image",
      color: "hsl(38, 92%, 50%)",
      rows: "350",
    },
  ];

  const onLoadDatasets = async () => {
    await getDatasetsUseCase.execute();
  };

  const loadDatasets = async () => {
    isLoadingDatasets.value = true;

    await onLoadDatasets();

    isLoadingDatasets.value = false;
  };

  return {
    datasets,
    isLoadingDatasets,
    getNewDatasetByRepoId,
    isAdminOrOwnerRole,
    exampleDatasets,
    error,
  };
};
