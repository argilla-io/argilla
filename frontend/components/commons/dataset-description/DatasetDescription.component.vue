<template>
  <div class="description">
    <h2 class="--heading5 --semibold description__title">{{ title }}</h2>
    <BaseSpinner v-if="isLoading" />
    <MarkdownEditorComponent
      v-if="!isLoading"
      :value="datasetGuidelines"
      placeholder="Insert here your guidelines"
      @save="updateGuidelines"
    />
  </div>
</template>

<script>
import { getDatasetFromORM } from "@/models/dataset.utilities";
import { Notification } from "@/models/Notifications";
import { mapActions } from "vuex";

export default {
  props: {
    datasetId: {
      type: Array,
      required: true,
    },
    datasetTask: {
      type: String,
      required: true,
    },
    isLoading: {
      type: Boolean,
      default: () => true,
    },
  },
  data() {
    return {
      title: "Description and annotation guidelines",
    };
  },
  computed: {
    dataset() {
      return getDatasetFromORM(this.datasetId, this.datasetTask, false);
    },
    datasetGuidelines() {
      if (this.dataset) {
        return this.dataset.guidelines
      }
      return ''
    },
  },
  methods: {
    ...mapActions({
      updateDatasetGuidelines: "entities/datasets/updateDatasetGuidelines",
    }),
    async updateGuidelines() {
      console.log('Saving guidelines')
      try {
        await this.updateDatasetGuidelines();
      }
      catch (e) {
        Notification.dispatch("notify", {
          message: 'Error when saving the dataset description and annotation guidelines.',
          type: "error",
        });
      }
    }
  },
};
</script>

<style lang="scss" scoped>
.description {
  &__text {
    color: $black-37;
  }
}
</style>
