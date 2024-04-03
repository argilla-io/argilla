import { useTranslate } from "~/v1/infrastructure/services/useTranslate";

export const useDatasetProgressViewModel = ({
  datasetId,
}: {
  datasetId: string;
}) => {
  const t = useTranslate();
  const totalRecords = 400;
  const progressRanges = [
    {
      id: "submitted",
      name: t("datasets.submitted"),
      color: "#0508D9",
      value: 200,
    },
    {
      id: "discarded",
      name: t("datasets.discarded"),
      color: "#b7b7b7",
      value: 25,
    },
    {
      id: "pending",
      name: t("datasets.pending"),
      color: "#f2f2f2",
      value: 175,
    },
  ];

  return {
    totalRecords,
    progressRanges,
  };
};
