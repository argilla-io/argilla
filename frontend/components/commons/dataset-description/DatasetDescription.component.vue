<template>
  <div class="description">
    <h2 class="--heading5 --semibold description__title">{{ title }}</h2>
    <div class="description__markdown" v-if="!isEditing">
      <!-- Markdown content here  -->
      <p class="--body1 description__text" v-html="description" />
      <BaseButton name="edit-button" @on-click="onEdit">
        <svgicon width="15" height="15" name="pen"></svgicon
      ></BaseButton>
    </div>
    <div class="description__markdown__edit" v-if="isEditing">
      <!-- Markdown input component here -->

      <div class="description__button-area">
        <BaseButton name="save-button" class="primary small" @on-click="onSave"
          >Save</BaseButton
        >
        <BaseButton
          name="close-button"
          class="secondary small"
          @on-click="onClose"
          >Discard</BaseButton
        >
      </div>
    </div>
  </div>
</template>

<script>
import { getDatasetDescription, saveDescription } from "./MockedService";

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
  },
  data: () => {
    return {
      title: "Description and annotation guidelines",
      isEditing: false,
    };
  },
  computed: {
    description() {
      return getDatasetDescription(this.datasetId, this.datasetTask, false);
    },
  },
  methods: {
    onEdit() {
      this.isEditing = true;
    },
    async onSave() {
      await saveDescription(
        this.datasetId,
        this.datasetTask,
        "TEMPORAL_TODO_REMOVE"
      );

      this.isEditing = false;
    },
    onClose() {
      this.isEditing = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.description {
  &__text {
    color: $black-37;
    width: 90%;
  }

  &__markdown {
    display: flex;
    flex-direction: row;
    align-items: baseline;
    justify-content: space-between;
  }

  &__button-area {
    display: flex;
    justify-content: row;
    justify-content: flex-end;
    gap: 5px;
    margin-bottom: 5px;
  }
}
</style>
