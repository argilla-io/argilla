import { useResolve } from "ts-injecty";
import { onBeforeMount, ref } from "vue";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";
import { JobId } from "~/v1/domain/services/IDatasetRepository";
import { ExportDatasetToHubUseCase } from "~/v1/domain/usecases/export-dataset-to-hub-use-case";
import { JobRepository } from "~/v1/infrastructure/repositories";
import { useDebounce, useLocalStorage } from "~/v1/infrastructure/services";

interface ExportToHubProps {
  dataset: Dataset;
}

export const useExportToHubViewModel = (props: ExportToHubProps) => {
  const { dataset } = props;
  const exportToHubUseCase = useResolve(ExportDatasetToHubUseCase);

  const debounce = useDebounce(3000);
  const jobRepository = useResolve(JobRepository);
  const storage = useLocalStorage();

  const datasetExporting =
    storage.get<Record<string, string>>("datasetExportJobIds") ?? {};

  const isExporting = ref(!!datasetExporting[dataset.id]);

  const verifyExportStatus = async (jobId: JobId) => {
    try {
      if (!jobId) return;

      const job = await jobRepository.getJobStatus(jobId);

      isExporting.value = job.isRunning;

      if (!job.isRunning) {
        delete datasetExporting[dataset.id];

        storage.set("datasetExportJobIds", datasetExporting);
      }
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
        name: dataset.name,
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
