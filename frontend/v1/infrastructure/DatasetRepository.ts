import {
	URL_GET_V1_DATASETS,
	URL_GET_WORKSPACES,
} from "~/utils/url.properties";
import { Dataset } from "../domain/entities/Dataset";
import { IDatasetRepository } from "../domain/services/IDatasetRepository";
import { upsertDataset } from "~/models/dataset.utilities";
import { upsertFeedbackDataset } from "~/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";
import { NuxtAxiosInstance } from "@nuxtjs/axios";

export const TYPE_OF_FEEDBACK = {
	ERROR_FETCHING_FEEDBACK_DATASETS: "ERROR_FETCHING_FEEDBACK_DATASETS",
	ERROR_FETCHING_WORKSPACES: "ERROR_FETCHING_WORKSPACES",
	ERROR_FETCHING_DATASET_INFO: "ERROR_FETCHING_DATASET_INFO",
	ERROR_FETCHING_WORKSPACE_INFO: "ERROR_FETCHING_WORKSPACE_INFO",
};
export class DatasetRepository implements IDatasetRepository {
	constructor(
		private readonly axios: NuxtAxiosInstance,
		private readonly fetchDatasets: () => Promise<any>
	) {}

	async getDatasetInfo(datasetId) {
		try {
			const { data } = await this.axios.get(`/v1/datasets/${datasetId}`);

			return data;
		} catch (err) {
			throw {
				response: TYPE_OF_FEEDBACK.ERROR_FETCHING_DATASET_INFO,
			};
		}
	}

	async getWorkspaceInfo(workspaceId) {
		try {
			const { data: responseWorkspace } = await this.axios.get(
				`/v1/workspaces/${workspaceId}`
			);

			const { name } = responseWorkspace || { name: null };

			return name;
		} catch (err) {
			throw {
				response: TYPE_OF_FEEDBACK.ERROR_FETCHING_WORKSPACE_INFO,
			};
		}
	}

	async getById(id: string): Promise<Dataset> {
		const dataset = await this.getDatasetInfo(id);
		const workspace = await this.getWorkspaceInfo(dataset.workspace_id);

		upsertFeedbackDataset({ ...dataset, workspace_name: workspace });

		return new Dataset(
			dataset.id,
			dataset.name,
			dataset.guidelines,
			dataset.status,
			dataset.workspace_id,
			workspace,
			dataset.inserted_at,
			dataset.updated_at
		);
	}

	async getAll(): Promise<Dataset[]> {
		const response = await this.saveAndGetDatasets();

		return response.feedbackDatasetsWithWorkspaces.map((datasetFromBackend) => {
			return new Dataset(
				datasetFromBackend.id,
				datasetFromBackend.name,
				datasetFromBackend.guidelines,
				datasetFromBackend.status,
				datasetFromBackend.workspace_id,
				datasetFromBackend.workspace_name,
				datasetFromBackend.inserted_at,
				datasetFromBackend.updated_at
			);
		});
	}

	fetchFeedbackDatasets = async (axios) => {
		const url = URL_GET_V1_DATASETS;
		try {
			const { data } = await axios.get(url);

			return data;
		} catch (err) {
			throw {
				response: TYPE_OF_FEEDBACK.ERROR_FETCHING_FEEDBACK_DATASETS,
			};
		}
	};

	fetchWorkspaces = async (axios) => {
		const url = URL_GET_WORKSPACES;
		try {
			const { data } = await axios.get(url);

			return data;
		} catch (err) {
			throw {
				response: TYPE_OF_FEEDBACK.ERROR_FETCHING_WORKSPACES,
			};
		}
	};

	factoryFeedbackDatasetsWithCorrespondingWorkspaceName = (
		feedbackDatasets,
		workspaces
	) => {
		const newFeedbackDatasets = feedbackDatasets.map((feedbackDataset) => {
			return {
				...feedbackDataset,
				workspace_name:
					workspaces.find(
						(workspace) => workspace.id === feedbackDataset.workspace_id
					)?.name || "",
			};
		});
		return newFeedbackDatasets;
	};

	saveAndGetDatasets = async () => {
		// FETCH old list of datasets (Text2Text, TextClassification, TokenClassification)
		const oldDatasets = await this.fetchDatasets();

		// FETCH new FeedbackTask list
		const { items: feedbackTaskDatasets } = await this.fetchFeedbackDatasets(
			this.axios
		);

		// TODO - remove next line when workspace will be include in the api endpoint to fetch feedbackTask
		const workspaces = await this.fetchWorkspaces(this.axios);

		const feedbackDatasetsWithWorkspaces =
			this.factoryFeedbackDatasetsWithCorrespondingWorkspaceName(
				feedbackTaskDatasets,
				workspaces
			);

		// UPSERT old dataset (Text2Text, TextClassification, TokenClassification) into the old orm
		upsertDataset(oldDatasets);

		// TODO - when workspaces will be include in feedbackDatasets, upsert directly "feedbackTaskDatasets" instead of "feedbackDatasetsWithWorkspaces"
		// UPSERT FeedbackDataset into the new orm for this task
		upsertFeedbackDataset(feedbackDatasetsWithWorkspaces);

		return { oldDatasets, feedbackDatasetsWithWorkspaces };
	};
}
