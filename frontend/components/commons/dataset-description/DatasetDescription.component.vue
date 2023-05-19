<template>
  <div class="description">
    <h2 class="--heading5 --semibold description__title">{{ title }}</h2>
    <div class="description__markdown" v-if="!isEditing">
      <!-- Markdown content here  -->
      <p class="--body1 description__text" v-html="description" />
      <BaseButton id="onEdit" @on-click="onEdit">
        <svgicon width="15" height="15" name="pen"></svgicon
      ></BaseButton>
    </div>
    <div class="description__markdown__edit" v-if="isEditing">
      <!-- Markdown input component here -->

      <div class="description__button-area">
        <base-button id="onSave" class="primary small" @on-click="onSave"
          >Save</base-button
        >
        <base-button id="onClose" class="secondary small" @on-click="onClose"
          >Discard</base-button
        >
      </div>
    </div>
  </div>
</template>

<script>
import { getDatasetFromORM } from "@/models/dataset.utilities";
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
    dataset() {
      return getDatasetFromORM(this.datasetId, this.datasetTask, false);
    },
    description() {
      return this.dataset?.tags.description;
    },
  },
  methods: {
    onEdit() {
      this.isEditing = true;
    },
    onSave() {
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
    align-items: center;
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
