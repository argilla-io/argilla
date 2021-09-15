<template>
  <div>
    <div v-if="annotation.length">
      <text-2-text-list :list="annotation" :editable="true" @input="onInput" />
    </div>
    <div v-else-if="prediction.length">
      <text-2-text-list :list="prediction" :editable="true" @input="onInput" />
    </div>
    <div v-else>
      <text-2-text-list :list="[]" :editable="true" @input="onInput" />
    </div>
    <re-button class="button button-primary" @click="annotate"
      >Validate</re-button
    >
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
    newSentence: undefined,
  }),
  methods: {
    onInput(sentence) {
      this.newSentence = sentence;
    },
    annotate() {
      if (this.newSentence) {
        let newS = {
          score: 1,
          text: this.newSentence,
        };
        this.$emit("annotate", { sentences: [newS] });
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.button {
  display: block;
}
</style>
