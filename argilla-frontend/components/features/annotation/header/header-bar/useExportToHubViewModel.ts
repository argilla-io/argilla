import { useResolve } from "ts-injecty";
import { onBeforeMount, ref, set } from "vue";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";
import { JobId } from "~/v1/domain/services/IDatasetRepository";
import { ExportDatasetToHubUseCase } from "~/v1/domain/usecases/export-dataset-to-hub-use-case";
import { JobRepository } from "~/v1/infrastructure/repositories";
import {
  useDebounce,
  useLocalStorage,
  useNotifications,
} from "~/v1/infrastructure/services";

interface ExportToHubProps {
  dataset: Dataset;
}

export const useExportToHubViewModel = (props: ExportToHubProps) => {
  const { dataset } = props;
  const notify = useNotifications();
  const debounce = useDebounce(3000);
  const { get, set } = useLocalStorage();

  const exportToHubUseCase = useResolve(ExportDatasetToHubUseCase);
  const jobRepository = useResolve(JobRepository);

  const datasetExporting =
    get<Record<string, string>>("datasetExportJobIds") ?? {};
  const isExporting = ref(!!datasetExporting[dataset.id]);

  const verifyExportStatus = async (jobId: JobId) => {
    try {
      if (!jobId) return;

      const job = await jobRepository.getJobStatus(jobId);

      isExporting.value = job.isRunning;

      if (!job.isRunning) {
        delete datasetExporting[dataset.id];

        set("datasetExportJobIds", datasetExporting);
      }

      notify.notify({
        type: job.isFinished ? "success" : "danger",
        message: job.isFinished ? "Dataset exported to Hub" : "Export failed",
        buttonText: "Go to Hub",
        onClick: job.isFinished
          ? () => {
              window.open("https://hub.huggingface.co/datasets", "_blank");
            }
          : undefined,
        permanent: true,
      });
    } catch {}
  };

  const watchExportStatus = async () => {
    while (datasetExporting[dataset.id]) {
      await debounce.wait();

      await verifyExportStatus(datasetExporting[dataset.id]);
    }

    debounce.stop();
  };

  const exportToHub = async () => {
    try {
      isExporting.value = true;

      await exportToHubUseCase.execute(dataset, {
        name: `${localStorage.getItem("hfUsername") ?? ""}/${dataset.name}`, // Temporal, add just for testing
        isPrivate: false,
        hfToken: localStorage.getItem("hfToken") ?? "", // Temporal, add just for testing
      });

      watchExportStatus();
    } catch {
      isExporting.value = false;
    }
  };

  onBeforeMount(() => {
    watchExportStatus();
  });

  return {
    isExporting,
    exportToHub,
  };
};
