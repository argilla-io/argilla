<template>
  <div class="dataset-config">
    <HorizontalResizable
      :min-height-percent="30"
      :id="`dataset-config-r-h-rz`"
      class="wrapper"
    >
      <template #up>
        <VerticalResizable :id="`dataset-config-left-t-v-rz`">
          <template #left>
            <div class="dataset-config__fields">
              <Record
                v-if="firstRecord"
                :recordCriteria="{
                  committed: {
                    searchText: {
                      value: {
                        text: {
                          text: '',
                        },
                      },
                    },
                  },
                }"
                :record="{
                  fields: Object.entries(firstRecord)
                    .filter(([name]) => name !== dataset.mappings.external_id)
                    .map(([name, content]) => ({
                      name,
                      title: name,
                      content: `${content}`,
                      settings: {},
                    })),
                }"
              />
            </div>
          </template>
          <template #right>
            <div class="dataset-config__questions-wrapper">
              <p
                v-if="!dataset.questions.length"
                class="dataset-config__empty-questions"
                v-text="'Your question will be here'"
              />

              <QuestionsComponent
                class="dataset-config__questions"
                v-else
                :questions="dataset.questions"
              />
            </div>
          </template>
        </VerticalResizable>
      </template>
      <template #down>
        <VerticalResizable
          class="dataset-config__down"
          :id="`dataset-preview-t-v-rz`"
        >
          <template #left>
            <div class="dataset-config__preview">
              <iframe
                v-if="!!dataset.repoId"
                :src="`https://huggingface.co/datasets/${dataset.repoId}/embed/viewer/ParaphraseRC/train`"
                frameborder="0"
                width="100%"
                height="500px"
              ></iframe>
            </div>
          </template>
          <template #right>
            <div class="dataset-config__configuration">
              <DatasetConfigurationForm
                :dataset="dataset"
                @change-subset="$emit('change-subset', $event)"
                @change-split="$emit('change-split', $event)"
              />
            </div>
          </template>
        </VerticalResizable>
      </template>
    </HorizontalResizable>
  </div>
</template>

<script>
import { useDatasetConfiguration } from "./useDatasetConfiguration";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  mounted() {
    this.getFirstRecord(this.dataset);
  },
  setup() {
    return useDatasetConfiguration();
  },
};
</script>

<style scoped lang="scss">
.wrapper {
  @include media("<desktop") {
    overflow: auto;
  }
}
.dataset-config {
  height: 100%;
  min-height: 0;
  &__fields {
    width: 100%;
    height: 100%;
    padding: $base-space * 2;
  }
  &__down {
    display: flex;
    height: 100%;
    width: 100%;
  }
  &__preview {
    align-items: flex-start;
    justify-items: center;
    padding: $base-space * 2;
    width: 40vw;
    height: 100%;
    overflow: auto;
  }
  &__empty-questions {
    width: 100%;
    text-align: center;
    padding: $base-space * 4;
    color: var(--fg-secondary);
    background-color: var(--bg-accent-grey-1);
    border: 1px dashed var(--bg-opacity-10);
    border-radius: $border-radius-m;
    margin: 0;
    @include font-size(16px);
  }
  &__questions-wrapper {
    width: 100%;
    height: 100%;
    padding: $base-space * 2;
    overflow: auto;
  }
  &__questions {
    background: var(--bg-form);
    border: 1px solid var(--bg-opacity-6);
    border-radius: $border-radius-m;
    display: flex;
    flex-direction: column;
    gap: $base-space * 2;
    overflow: auto;
    padding: $base-space * 2;
    position: relative;
    scroll-behavior: smooth;
  }
  &__configuration {
    width: 100%;
    height: 100%;
  }
}
</style>
