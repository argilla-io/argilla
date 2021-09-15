<template>
  <div>
    <re-tabs @change-tab="onChangeTab" :tabs="['Prediction', 'Annotation']" :activeTab="showTab">
      <div class="content">
        <template v-if="showTab === 'Prediction'">
          <span v-for="(sentence, index) in prediction" :key="index">
            {{sentence.text}} <p><strong>Score: {{sentence.score}}</strong></p>
          </span>
        </template>
        <template v-if="showTab === 'Annotation'">
          <span v-for="(sentence, index) in annotation" :key="index">
            {{sentence.text}} <p><strong>Score: {{sentence.score}}</strong></p>
          </span>
        </template>
      </div>
    </re-tabs>
  </div>
</template>
<script>

export default {
  props: {
    annotation: {
      type: Array,
      required: true,
    },
    prediction: {
      type: Array,
      required: true,
    },
  },
  data: () => ({
    showTab: 'Prediction',
  }),
  methods: {
    onChangeTab(tab) {
      this.showTab = tab
    }
  }
};
</script>
<style lang="scss" scoped>
.content {
  border: 1px solid $primary-color;
  padding: 1em;
}
</style>
