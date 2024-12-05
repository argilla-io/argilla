import { useResolve } from "ts-injecty";
import { onBeforeMount, ref, computed } from "vue";
import { Dataset } from "~/v1/domain/entities/dataset/Dataset";
import { ExportDatasetToHubUseCase } from "~/v1/domain/usecases/export-dataset-to-hub-use-case";
import { JobRepository } from "~/v1/infrastructure/repositories";
import {
  useDebounce,
  useLocalStorage,
  useNotifications,
  useUser,
} from "~/v1/infrastructure/services";

interface ExportToHubProps {
  dataset: Dataset;
}

export const useExportToHubViewModel = (props: ExportToHubProps) => {
  const { dataset } = props;
  const { user } = useUser();
  const notify = useNotifications();
  const debounce = useDebounce(3000);
  const { get, set } = useLocalStorage();

  const isDialogOpen = ref(false);
  const errors = ref({});
  const exportToHubForm = ref({
    orgOrUsername: "",
    datasetName: "",
    hfToken: "",
    isPrivate: false,
  });

  const exportToHubUseCase = useResolve(ExportDatasetToHubUseCase);
  const jobRepository = useResolve(JobRepository);

  const validate = () => {
    const validations = {
      orgOrUsername: [],
      datasetName: [],
      hfToken: [],
    };
    if (!exportToHubForm.value.orgOrUsername) {
      validations.orgOrUsername.push(
        "exportToHub.validations.orgOrUsernameIsRequired"
      );
    }
    if (!exportToHubForm.value.datasetName) {
      validations.datasetName.push(
        "exportToHub.validations.datasetNameIsRequired"
      );
    }
    if (!exportToHubForm.value.hfToken) {
      validations.hfToken.push("exportToHub.validations.hfTokenIsRequired");
    }
    return validations;
  };

  const validateForm = (input: string) => {
    errors.value[input] = validate()[input];
  };

  const isValid = computed(() => {
    const validations = validate();
    return (
      validations.orgOrUsername.length === 0 &&
      validations.datasetName.length === 0 &&
      validations.hfToken.length === 0
    );
  });

  const getDatasetExporting = () =>
    get<
      Record<
        string,
        {
          jobId: string;
          datasetName: string;
        }
      >
    >("datasetExportJobIds") ?? {};

  const isExporting = ref(!!getDatasetExporting()[dataset.id]);

  const verifyExportStatus = async () => {
    try {
      const datasetExporting = getDatasetExporting();
      const exporting = datasetExporting[dataset.id];

      if (!exporting) return;

      const { jobId, datasetName } = exporting;

      const job = await jobRepository.getJobStatus(jobId);

      if (job.isRunning) return;

      isExporting.value = job.isRunning;

      delete datasetExporting[dataset.id];

      set("datasetExportJobIds", datasetExporting);

      notify.notify({
        type: job.isFinished ? "success" : "danger",
        message: job.isFinished ? "Dataset exported to Hub" : "Export failed",
        buttonText: job.isFinished ? "Go to Hub" : undefined,
        onClick: job.isFinished
          ? () => {
              window.open(
                `https://huggingface.co/datasets/${datasetName}`,
                "_blank"
              );
            }
          : undefined,
        permanent: true,
      });
    } catch {}
  };

  const watchExportStatus = async () => {
    while (isExporting.value) {
      await debounce.wait();

      await verifyExportStatus();
    }

    debounce.stop();
  };

  const exportToHub = async () => {
    try {
      isExporting.value = true;

      await exportToHubUseCase.execute(dataset, {
        name: `${exportToHubForm.value.orgOrUsername}/${exportToHubForm.value.datasetName}`,
        isPrivate: exportToHubForm.value.isPrivate,
        hfToken: exportToHubForm.value.hfToken,
      });

      watchExportStatus();
    } catch {
      closeDialog();
      isExporting.value = false;
    }
  };

  const openDialog = () => {
    exportToHubForm.value = {
      orgOrUsername: user.value.userName,
      datasetName: dataset.name,
      hfToken: "",
      isPrivate: false,
    };

    isDialogOpen.value = true;
  };

  const closeDialog = () => {
    isDialogOpen.value = false;
  };

  onBeforeMount(() => {
    watchExportStatus();
  });

  return {
    isDialogOpen,
    closeDialog,
    openDialog,
    isExporting,
    exportToHub,
    exportToHubForm,
    validateForm,
    errors,
    isValid,
  };
};
