import { useLanguageDetector } from "./useLanguageDetector";

describe("useLanguageDetector", () => {
  const context = {
    app: {
      i18n: {
        locales: [{ code: "en" }, { code: "es" }, { code: "fr-CA" }],
        setLocale: jest.fn(),
      },
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("initialize should", () => {
    test("change to the detected language when it exists", () => {
      Object.defineProperty(window.navigator, "language", {
        value: "fr-CA",
        configurable: true,
      });

      const { initialize } = useLanguageDetector(context);

      initialize();

      expect(context.app.i18n.setLocale).toHaveBeenCalledWith("fr-CA");
    });

    test("change to base language code if not exist the complete code into locales", () => {
      Object.defineProperty(window.navigator, "language", {
        value: "es-AR",
        configurable: true,
      });

      const { initialize } = useLanguageDetector(context);

      initialize();

      expect(context.app.i18n.setLocale).toHaveBeenCalledWith("es");
    });

    test("not change to the language code when the detected language does not exist", () => {
      Object.defineProperty(window.navigator, "language", {
        value: "de",
        configurable: true,
      });

      const { initialize } = useLanguageDetector(context);

      initialize();

      expect(context.app.i18n.setLocale).toHaveBeenCalledTimes(0);
    });
  });
});
