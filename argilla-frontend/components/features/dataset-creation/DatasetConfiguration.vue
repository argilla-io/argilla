<template>
  <div class="dataset-config">
    <HorizontalResizable :id="`dataset-config-r-h-rz`">
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
            <DatasetConfigurationSelector
              :options="datasetConfig.subsets"
              :value="datasetConfig.selectedSubset.name"
              @onValueChange="$emit('change-subset', $event)"
            />
            {{ datasetConfig.selectedSubset }}
          </template>
          <template #right>
            <!-- <QuestionsComponent
              v-if="!!questions"
              :questions="questions"
            /> -->
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
              :fields="datasetConfig.fields"
              :questions="datasetConfig.questions"
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
  &__configuration {
    width: 100%;
    height: 100%;
    overflow: auto;
  }
  &__preview {
    align-items: flex-start;
    justify-items: center;
    padding: $base-space * 2;
    min-width: 40vw;
    height: 100%;
    overflow: auto;
  }
}
</style>
