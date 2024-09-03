import { useContext, useRoute, useRouter } from "@nuxtjs/composition-api";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";

type KindOfParam =
  | "status"
  | "page"
  | "search"
  | "metadata"
  | "sort"
  | "response"
  | "suggestion"
  | "similarity"
  | "tab";

type QueryParam = {
  key: KindOfParam;
  value: string;
  encode?: boolean;
};

export const ROUTES = {
  signIn: "/sign-in",
  datasets: "datasets",
  annotationPage: (datasetId: string) =>
    `/dataset/${datasetId}/annotation-mode`,
  settings: (id: string) => `/dataset/${id}/settings`,
};

export const useRoutes = () => {
  const context = useContext();
  const router = useRouter();
  const route = useRoute();

  const getPreviousRoute = (): string => {
    return context.from.value.fullPath;
  };

  const previousRouteMatchWith = (value: string): boolean => {
    const previousRoute = getPreviousRoute();
    const currentRoute = route.value.fullPath;

    if (previousRoute !== currentRoute) return previousRoute.includes(value);

    return false;
  };

  const getDatasetLink = ({ id }: Dataset): string => {
    return ROUTES.annotationPage(id);
  };

  const goToFeedbackTaskAnnotationPage = (datasetId: string) => {
    router.push(ROUTES.annotationPage(datasetId));
  };

  const goToSetting = (id: string) => {
    router.push(ROUTES.settings(id));
  };

  const goToDatasetsList = () => {
    router.push({ path: `/${ROUTES.datasets}` });
  };

  const goToSignIn = () => {
    router.push(ROUTES.signIn);
  };

  const setQueryParams = async (...params: QueryParam[]) => {
    const actualQuery = route.value.query;
    const funcToUse = Object.keys(actualQuery).length ? "push" : "replace";
    let newQuery = {};

    params.forEach(({ key, value }) => {
      if (!value) return;

      newQuery = {
        ...newQuery,
        [key]: encodeURIComponent(value),
      };
    });

    await router[funcToUse]({
      path: route.value.path,
      query: {
        ...newQuery,
      },
    });
  };

  const setQueryParamsVirtually = (...params: QueryParam[]) => {
    let newQuery = {};

    params.forEach(({ key, value }) => {
      if (!value) return;

      newQuery = {
        ...newQuery,
        [key]: encodeURIComponent(value),
      };
    });

    const url = new URL(window.location.href);
    url.search = new URLSearchParams(newQuery).toString();

    window.history.replaceState(null, "", url.toString());
  };

  const getQueryParams = <T>(key: KindOfParam): T => {
    const value = route.value.query[key] as string;
    if (!value) return;

    return decodeURIComponent(value) as T;
  };

  const getParams = () => {
    return route.value.params;
  };

  const go = (
    where: string,
    params: { external: boolean; newWindow: boolean } = {
      external: false,
      newWindow: false,
    }
  ) => {
    if (params.external) {
      if (params.newWindow) {
        window.open(where);
      } else {
        window.location.href = where;
      }
    }

    router.push(where);
  };

  const getQuery = () => {
    return route.value.query;
  };

  const goBack = () => {
    router.go(-1);
  };

  return {
    go,
    goBack,
    goToSignIn,
    getQuery,
    goToFeedbackTaskAnnotationPage,
    goToDatasetsList,
    goToSetting,
    getDatasetLink,
    setQueryParams,
    setQueryParamsVirtually,
    getQueryParams,
    getParams,
    getPreviousRoute,
    previousRouteMatchWith,
    watchBrowserNavigation: (callBack: () => void) => {
      window.addEventListener("popstate", callBack);
    },
  };
};
