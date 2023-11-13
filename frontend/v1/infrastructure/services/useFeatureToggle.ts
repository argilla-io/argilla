type FF = "metadata-filter-delay" | "sort-delay";
type Cast = "integer";

const settings = localStorage.getItem("argilla-dev");

export const useFeatureToggle = () => {
  const getValue = (key: FF, cast: Cast) => {
    if (!settings) return null;

    const parsed = JSON.parse(settings);

    switch (cast) {
      case "integer":
        return parseInt(parsed[key]);
      default:
        return parsed[key];
    }
  };

  return { getValue };
};
