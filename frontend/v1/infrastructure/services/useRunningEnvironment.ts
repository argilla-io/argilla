import { useResolve } from "ts-injecty";
import { OAuthLoginUseCase } from "~/v1/domain/usecases/oauth-login-use-case";

interface HFSpace {
  space: string;
  user: string;
}

const HUGGING_FACE_EMBEBED_URL = "huggingface.co";
const HUGGING_FACE_DIRECT_URL = ".hf.space";
const HUGGING_FACE_TOKEN_COOKIE = "spaces-jwt";

const parseJwt = (token: string) => {
  try {
    return JSON.parse(atob(token.split(".")[1]));
  } catch (e) {
    return null;
  }
};

export const useRunningEnvironment = () => {
  const url = new URL(window.location.href);

  const isEmbebed = () => {
    return window.self !== window.top;
  };

  const getHuggingFaceInfo = (): HFSpace | null => {
    if (!isRunningOnHuggingFace()) return null;

    const splitted = document.cookie.split(";");
    const hfCookie = splitted.find((c) => {
      return c.includes(HUGGING_FACE_TOKEN_COOKIE);
    });

    if (!hfCookie) return null;

    const token = hfCookie.split("=")[1];

    const parsed = parseJwt(token);

    if (!parsed) return null;

    const [user, space] = parsed.sub
      .replace("/spaces/", "")
      .split("/")
      .filter(Boolean);

    return {
      user,
      space,
    };
  };

  const isRunningOnHuggingFace = (): boolean => {
    return (
      url.host === HUGGING_FACE_EMBEBED_URL ||
      url.host.endsWith(HUGGING_FACE_DIRECT_URL)
    );
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
    getHuggingFaceInfo,
  };
};
