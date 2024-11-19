import { useLanguageDetector } from "./useLanguageDetector";
import { useLocalStorage } from "./useLocalStorage";

jest.mock("./useLocalStorage");
const useLocalStorageMock = jest.mocked(useLocalStorage);

describe("useLanguageDetector", () => {
  const context = {
    app: {
      i18n: {
        locales: [{ code: "en" }, { code: "es" }, { code: "fr" }],
        setLocale: jest.fn(),
      },
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("initialize should", () => {
    test("set the browser language if the user does not have the language saved and the browser language is supported", () => {
      Object.defineProperty(window.navigator, "language", {
        value: "es",
        configurable: true,
      });
      useLocalStorageMock.mockReturnValue({
        get: jest.fn().mockReturnValue(null),
        pop: jest.fn(),
        set: jest.fn(),
      });

      const { initialize } = useLanguageDetector(context);

      initialize();

      expect(context.app.i18n.setLocale).toHaveBeenCalledWith("es");
    });

    test("set the browser language if the user does not have the language saved and the browser language is supported", () => {
      Object.defineProperty(window.navigator, "language", {
        value: "es-AR",
        configurable: true,
      });
      useLocalStorageMock.mockReturnValue({
        get: jest.fn().mockReturnValue(null),
        pop: jest.fn(),
        set: jest.fn(),
      });

      const { initialize } = useLanguageDetector(context);

      initialize();

      expect(context.app.i18n.setLocale).toHaveBeenCalledWith("es");
    });

    test("set English if the user does not have the language saved and the browser language is not supported", () => {
      Object.defineProperty(window.navigator, "language", {
        value: "de",
        configurable: true,
      });
      useLocalStorageMock.mockReturnValue({
        get: jest.fn().mockReturnValue(null),
        pop: jest.fn(),
        set: jest.fn(),
      });

      const { initialize } = useLanguageDetector(context);

      initialize();

      expect(context.app.i18n.setLocale).toHaveBeenCalledWith("en");
    });

    test("set the language saved by the user", () => {
      useLocalStorageMock.mockReturnValue({
        get: () => "fr",
        pop: jest.fn(),
        set: jest.fn(),
      });

      const { initialize } = useLanguageDetector(context);

      initialize();

      expect(context.app.i18n.setLocale).toHaveBeenCalledWith("fr");
    });
  });
});
