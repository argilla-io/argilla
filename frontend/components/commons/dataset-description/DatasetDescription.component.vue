<template>
  <div>
    <h2 class="--heading5 --semibold description__title">{{ title }}</h2>
    <EditableDescriptionMarkdown :description="description" @onSave="onSave" />
  </div>
</template>

<script>
import EditableDescriptionMarkdown from "./EditableDescriptionMarkdown.component.vue";

import { getDatasetDescription, saveDescription } from "./MockedService";

export default {
  components: {
    EditableDescriptionMarkdown,
  },
  props: {
    datasetId: {
      type: Array,
      required: true,
    },
    datasetTask: {
      type: String,
      required: true,
    },
  },
  data: () => {
    return {
      title: "Description and annotation guidelines",
    };
  },
  computed: {
    description() {
      return getDatasetDescription(this.datasetId, this.datasetTask);
    },
  },
  methods: {
    onSave(newDescription) {
      saveDescription(this.datasetId, this.datasetTask, newDescription);
    },
  },
};
</script>