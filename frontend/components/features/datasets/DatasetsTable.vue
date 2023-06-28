<template>
	<div class="container">
		<datasets-empty v-if="!datasets.length" />
		<div v-else>
			<div class="interactions">
				<base-search-bar @input="onSearch" placeholder="Search datasets" />
			</div>
			<base-table-info
				ref="table"
				search-on="name"
				:global-actions="false"
				:data="datasets"
				:sorted-order="sortedOrder"
				:sorted-by-field="sortedByField"
				:actions="actions"
				:columns="tableColumns"
				:query-search="querySearch"
				:empty-search-info="emptySearchInfo"
				:active-filters="activeFilters"
				@sort-column="onSortColumns"
				@onActionClicked="onActionClicked"
				@filter-applied="onColumnFilterApplied"
			/>
		</div>
	</div>
</template>

<script lang="ts">
import { Base64 } from "js-base64";
import { currentWorkspace } from "@/models/Workspace";
import { Dataset } from "@/v1/domain/entities/Dataset";

export default {
	props: {
		datasets: {
			type: Array as () => Dataset[],
			required: true,
		},
	},
	data() {
		return {
			querySearch: undefined,
			tableColumns: [
				{
					name: "Name",
					field: "name",
					class: "table-info__title",
					type: "link",
				},
				{
					name: "Workspace",
					field: "workspace",
					class: "text",
					type: "text",
					filtrable: "true",
				},
				{
					name: "Task",
					field: "task",
					class: "task",
					type: "task",
					filtrable: "true",
				},
				{
					name: "Tags",
					field: "tags",
					class: "text",
					type: "object",
					filtrable: "true",
				},
				{
					name: "Created at",
					field: "created_at",
					class: "date",
					type: "date",
					sortable: "true",
				},
				{
					name: "Updated at",
					field: "last_updated",
					class: "date",
					type: "date",
					sortable: "true",
				},
			],
			actions: [
				{
					name: "go-to-settings",
					icon: "settings",
					title: "Go to dataset settings",
					tooltip: "Dataset settings",
				},
				{
					name: "copy",
					icon: "link",
					title: "Copy url to clipboard",
					tooltip: "Copied",
				},
			],
			emptySearchInfo: {
				title: "0 datasets found",
			},
			externalLinks: [],
			sortedOrder: "desc",
			sortedByField: "last_updated",
		};
	},
	computed: {
		activeFilters() {
			const workspaces = this.workspaces;
			const tasks = this.tasks;
			const tags = this.tags;
			return [
				{ column: "workspace", values: workspaces || [] },
				{ column: "task", values: tasks || [] },
				{ column: "tags", values: tags || [] },
			];
		},
		workspaces() {
			let _workspaces = this.$route.query.workspace;
			if (typeof _workspaces == "string") {
				_workspaces = [_workspaces];
			}
			return _workspaces;
		},
		tasks() {
			let _tasks = this.$route.query.task;
			if (typeof _tasks == "string") {
				_tasks = [_tasks];
			}
			return _tasks;
		},
		tags() {
			let _tags = this.$route.query.tags
				? JSON.parse(Base64.decode(this.$route.query.tags))
				: undefined;
			if (typeof _tags == "string") {
				_tags = [_tags];
			}
			return _tags;
		},
		workspace() {
			return currentWorkspace(this.$route);
		},
	},
	methods: {
		clearFilters() {
			if (this.$refs.table) {
				this.activeFilters.forEach((filter) => {
					this.$refs.table.onApplyFilters({ field: filter.column }, []);
				});
				this.$router.push({ path: "/datasets" });
			}
		},
		onSearch(event) {
			this.querySearch = event;
		},
		onSortColumns(by, order) {
			this.sortedByField = by;
			this.sortedOrder = order;
		},
		onColumnFilterApplied({ column, values }) {
			if (column === "workspace") {
				if (values !== this.workspaces) {
					this.$router.push({
						query: { ...this.$route.query, workspace: values },
					});
				}
			}
			if (column === "task") {
				if (values !== this.tasks) {
					this.$router.push({ query: { ...this.$route.query, task: values } });
				}
			}
			if (column === "tags") {
				if (values !== this.tags) {
					this.$router.push({
						query: {
							...this.$route.query,
							tags: values.length
								? Base64.encodeURI(JSON.stringify(values))
								: undefined,
						},
					});
				}
			}
		},
		onActionClicked(action, dataset) {
			switch (action) {
				case "go-to-settings":
					this.goToSetting(dataset);
					break;
				case "copy":
					this.copyUrl(dataset);
					break;
				case "copy-name":
					this.copyName(dataset);
					break;
				default:
					console.warn(action);
			}
		},
		isOldTask(task) {
			// NOTE - we need to detect old/new task because the redirection corresponding pages does not have the same route
			return [
				"TokenClassification",
				"TextClassification",
				"Text2Text",
			].includes(task);
		},
		copy(value) {
			this.$copyToClipboard(value);
		},
		copyUrl({ task, id, workspace, name }) {
			const isOldTask = this.isOldTask(task);

			const url = isOldTask
				? `/datasets/${workspace}/${name}`
				: `/dataset/${id}/annotation-mode`;

			this.copy(`${window.origin}${url}`);
		},
		copyName({ name }) {
			this.copy(name);
		},
		goToSetting({ id, workspace, name, task }) {
			const isOldTask = this.isOldTask(task);

			if (isOldTask) {
				this.$router.push({
					name: "datasets-workspace-dataset-settings",
					params: {
						workspace,
						dataset: name,
					},
				});
			} else {
				this.$router.push({
					name: "dataset-id-settings",
					params: { id },
				});
			}
		},
	},
};
</script>

<style lang="scss" scoped>
.container {
	@extend %container;
	padding-top: 0.2em;
	padding-bottom: 0;
	padding-right: calc($sidebarMenuWidth + 4em);
	&--intro {
		padding-top: 2em;
		margin-bottom: 1.5em;
		&:after {
			border-bottom: 1px solid palette(grey, 700);
			content: "";
			margin-bottom: 1.5em;
			position: absolute;
			left: 0;
			right: 0;
		}
	}
}
.interactions {
	display: flex;
	align-items: flex-end;
	margin: 2em 0 1em 0;
}
</style>
