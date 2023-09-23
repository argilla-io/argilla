import { useRoute, useRouter } from "@nuxtjs/composition-api";
import { Dataset } from "@/v1/domain/entities/Dataset";

type KindOfParam = "_status" | "_page" | "_search" | "_metadata";

export const ROUTES = {
  datasets: "datasets",
};
export const useRoutes = () => {
  const router = useRouter();
  const route = useRoute();

  const isOldTask = (task: string) => {
    return ["TokenClassification", "TextClassification", "Text2Text"].includes(
      task
    );
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
    router.push({ path: `/${ROUTES.datasets}` });
  };

  const addQueryParam = async (key: KindOfParam, value: string) => {
    const newQuery = {
      [key]: value,
    };

    await router.push({
      path: route.value.path,
      query: {
        ...route.value.query,
        ...newQuery,
      },
    });
  };

  const removeQueryParam = async (key: KindOfParam) => {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { [key]: _, ...rest } = route.value.query;

    await router.push({
      path: route.value.path,
      query: {
        ...rest,
      },
    });
  };

  return {
    goToDatasetsList,
    goToSetting,
    getDatasetLink,
    addQueryParam,
    removeQueryParam,
  };
};
