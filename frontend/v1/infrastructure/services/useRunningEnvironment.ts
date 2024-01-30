import { useResolve } from "ts-injecty";
import { OAuthLoginUseCase } from "~/v1/domain/usecases/oauth-login-use-case";

interface HFSpace {
  space: string;
  user: string;
}

const HUGGING_FACE_URLS = [
  { url: "huggingface.co", embebed: true },
  { url: ".hf.space", embebed: false },
];

export const useRunningEnvironment = () => {
  const url = new URL(window.location.href);

  const parseHuggingFaceData = (data: string[]) => {
    const user = data[0];
    const space = data[1];

    if (data.length === 2 && user && space)
      return {
        space,
        user,
      };

    return undefined;
  };

  const isEmbebed = () => {
    const match = HUGGING_FACE_URLS.find(
      (h) => url.host === h.url || url.host.endsWith(h.url)
    );

    return match?.embebed;
  };

  const isRunningOnHuggingFace = (): HFSpace | undefined => {
    const match = HUGGING_FACE_URLS.find(
      (h) => url.host === h.url || url.host.endsWith(h.url)
    );

    if (!match) return undefined;

    if (match.embebed) {
      const paramsData = url.pathname
        .replace("/spaces", "")
        .split("/")
        .filter(Boolean);

      return parseHuggingFaceData(paramsData);
    }

    const paramsData = url.host
      .replaceAll(match.url, "")
      .split(/-(.*)/s)
      .filter(Boolean);

    return parseHuggingFaceData(paramsData);
  };

  const hasHuggingFaceOAuthConfigured = async (): Promise<boolean> => {
    const oauthUseCase = useResolve(OAuthLoginUseCase);

    const providers = await oauthUseCase.getProviders();

    return providers.some((p) => p.isHuggingFace);
  };

  return {
    isEmbebed,
    isRunningOnHuggingFace,
    hasHuggingFaceOAuthConfigured,
  };
};
