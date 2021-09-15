<template>
  <div>
    <div class="content" v-for="(sentence, index) in annotation" :key="index">
      <p contenteditable="true" @input="onInput">{{sentence.text}}</p>
    </div>
    <re-button class="button button-primary" @click="annotate">Save</re-button>
  </div>
</template>
<script>

export default {
  props: {
    annotation: {
      type: Array,
      required: true,
    },
  },
  data: () => ({
    newSentence: undefined,
  }),
  methods: {
    onInput(e) {
      this.newSentence = e.target.innerText;
    },
    annotate() {
      if (this.newSentence) {
        let newS = {
          score: 1,
          text: this.newSentence,
        }
        this.$emit("annotate", { sentences: [newS] });
      }
    },
  }
};
</script>
<style lang="scss" scoped>
.content {
  border: 1px solid $primary-color;
  font-family: monospace;
  margin-bottom: 1em;
  margin-top: 1em;
  p {
    padding: 1em;
    margin: 0;
    outline: none;
  }
}
.button {
  display: block;
}
</style>
