<template>
  <div class="description">
    <h2 class="--heading5 --semibold description__title">{{ title }}</h2>
    <div class="description__markdown__viewer" v-if="!isEditing">
      <span
        class="--body1 description__markdown__viewer-text"
        v-html="compiledDescription"
      />
      <BaseButton name="edit-button" @on-click="onEdit">
        <svgicon width="15" height="15" name="pen"></svgicon
      ></BaseButton>
    </div>
    <div class="description__markdown__editor" v-if="isEditing">
      <textarea
        name="description-input"
        class="description__markdown__editor-input"
        v-model="newDescription"
      ></textarea>

      <div class="description__markdown__editor-button-area">
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
import { marked } from "marked";

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
      newDescription: "",
    };
  },
  computed: {
    description() {
      return getDatasetDescription(this.datasetId, this.datasetTask);
    },
    compiledDescription() {
      return marked.parse(this.description);
    },
  },
  methods: {
    onEdit() {
      this.newDescription = this.description;

      this.isEditing = true;
    },
    async onSave() {
      await saveDescription(
        this.datasetId,
        this.datasetTask,
        this.newDescription
      );

      this.isEditing = false;
    },
    onClose() {
      this.newDescription = "";

      this.isEditing = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.description {
  &__markdown {
    margin-bottom: 5px;

    &__viewer {
      display: flex;
      flex-direction: row;
      align-items: baseline;
      justify-content: space-between;

      &-text {
        color: $black-37;
        width: 90%;
      }
    }

    &__editor {
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      margin-bottom: 1em;
      gap: 20px;

      &-button-area {
        display: flex;
        justify-content: row;
        justify-content: flex-end;
        gap: 5px;
      }

      &-input {
        width: 100%;
        min-height: 20vh;
        padding: 12px 20px;
        box-sizing: border-box;
        border: 2px solid #ccc;
        border-radius: 4px;
        background-color: #f8f8f8;
        resize: none;
      }
    }
  }
}
</style>
