<template>
  <div class="dataset-config">
    <HorizontalResizable :id="`dataset-config-r-h-rz`" class="wrapper">
      <template #up>
        <VerticalResizable :id="`dataset-config-left-t-v-rz`">
          <template #left>
            <!-- <div class="dataset-config__fields">
              <Record
                v-if="!!fields"
                :record="{
                  fields: fields,
                  questions: questions,
                }"
              />
            </div> -->
            <div :style="{ overflow: 'auto', height: '100%' }">
              <pre>{{ datasetConfig }}</pre>
            </div>
          </template>
          <template #right>
            <div class="dataset-config__questions-wrapper">
              <p
                v-if="!datasetConfig.questions.length"
                class="dataset-config__empty-questions"
                v-text="'Your question will be here'"
              />

              <QuestionsComponent
                class="dataset-config__questions"
                v-else
                :questions="datasetConfig.questions"
              />
            </div>
          </template>
        </VerticalResizable>
      </template>
      <template #down>
        <div class="dataset-config__down">
          <div class="dataset-config__preview">
            <iframe
              v-if="!!datasetId"
              :src="`https://huggingface.co/datasets/${datasetId}/embed/viewer/ParaphraseRC/train`"
              frameborder="0"
              width="100%"
              height="500px"
            ></iframe>
          </div>
          <div class="dataset-config__configuration">
            <DatasetConfigurationForm
              :subsets="datasetConfig.subsets"
              :selected-subset="datasetConfig.selectedSubset"
              :splits="datasetConfig.splits"
              :selected-split="datasetConfig.selectedSplit"
              :dataset-id="datasetId"
              @change-subset="$emit('change-subset', $event)"
              @change-split="$emit('change-split', $event)"
            />
          </div>
        </div>
      </template>
    </HorizontalResizable>
  </div>
</template>

<script>
export default {
  props: {
    datasetConfig: {
      type: Object,
      required: true,
    },
    datasetId: {
      type: String,
      required: true,
    },
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
    padding: $base-space * 2 $base-space $base-space * 2 $base-space * 2;
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
    min-width: 40vw;
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
  }
}
</style>
