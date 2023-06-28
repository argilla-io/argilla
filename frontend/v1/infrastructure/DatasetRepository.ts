import {
	URL_GET_V1_DATASETS,
	URL_GET_WORKSPACES,
} from "~/utils/url.properties";
import { Dataset } from "../domain/entities/Dataset";
import { IDatasetRepository } from "../domain/services/IDatasetRepository";
import { upsertDataset } from "~/models/dataset.utilities";
import { upsertFeedbackDataset } from "~/models/feedback-task-model/feedback-dataset/feedbackDataset.queries";
import { NuxtAxiosInstance } from "@nuxtjs/axios";

const TYPE_OF_FEEDBACK = {
	ERROR_FETCHING_FEEDBACK_DATASETS: "ERROR_FETCHING_FEEDBACK_DATASETS",
	ERROR_FETCHING_WORKSPACES: "ERROR_FETCHING_WORKSPACES",
};
export class DatasetRepository implements IDatasetRepository {
	constructor(
		private readonly axios: NuxtAxiosInstance,
		private readonly fetchDatasets: () => Promise<any>
	) {}

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
