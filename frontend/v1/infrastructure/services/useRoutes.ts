import { useRouter } from "@nuxtjs/composition-api";
import { Dataset } from "~/v1/domain/entities/Dataset";

export const useRoutes = () => {
  const router = useRouter();

  const isOldTask = (task: string) => {
    return ["TokenClassification", "TextClassification", "Text2Text"].includes(
      task
    );
  };

  const getDatasetLinkPage = ({ task, name, workspace, id }: Dataset) => {
    if (isOldTask(task))
      return {
        name: "datasets-workspace-dataset",
        params: {
          dataset: name,
          workspace,
        },
      };

    return {
      name: "dataset-id-annotation-mode",
      params: {
        id,
      },
    };
  };

  const getDatasetLink = ({ task, name, workspace, id }: Dataset): string => {
    return isOldTask(task)
      ? `/datasets/${workspace}/${name}`
      : `/dataset/${id}/annotation-mode`;
  };

  const goToSetting = ({ task, workspace, name, id }: Dataset) => {
    if (isOldTask(task)) {
      router.push({
        name: "datasets-workspace-dataset-settings",
        params: {
          workspace,
          dataset: name,
        },
      });
    } else {
      router.push({
        name: "dataset-id-settings",
        params: { id },
      });
    }
  };

  const goToDatasetsList = () => {
    router.push({ path: "/datasets" });
  };

  return { goToDatasetsList, getDatasetLinkPage, goToSetting, getDatasetLink };
};
