<template>
  <div class="wrapper">
    <QuestionHeaderComponent :question="question" />
    <div v-for="entity in question.answer.entities">
      <span
        v-text="entity.name"
        :style="{
          color: entity.color,
          backgroundColor: entity.isSelected ? 'lightgray' : 'white',
        }"
        @click="select(entity)"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: "SpanComponent",
  props: {
    question: {
      type: Object,
      required: true,
    },
  },
  methods: {
    select(entity) {
      this.question.answer.entities.forEach((e) => {
        e.isSelected = e.id === entity.id;
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: $base-space;
}
</style>
