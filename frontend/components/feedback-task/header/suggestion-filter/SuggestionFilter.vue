<template>
  <div>
    <h2>Suggestions</h2>
    <div v-if="!secondSection.length">
      <div v-for="question in questionFilters.questions">
        <p @click="changeToSecondSection(question)">{{ question.name }}</p>
      </div>
    </div>
    <div v-else>
      <div v-if="!thirdSection">
        <div v-for="config in secondSection">
          <p @click="changeToThirdSection(config)">{{ config.id }}</p>
        </div>
      </div>
      <div v-else>
        <div v-if="thirdSection.id === 'values'">
          {{ thirdSection.question.settings.type }}
          <div v-for="answer in thirdSection.question.answer.values">
            <p>{{ answer }}</p>
          </div>
          <div v-for="conditional in thirdSection.conditionals">
            <b>{{ conditional }}</b>
          </div>
        </div>
        <div v-if="thirdSection.id === 'score'">
          <p>{{ thirdSection.min }}</p>
          <p>{{ thirdSection.max }}</p>
        </div>
        <div v-if="thirdSection.id === 'agent'">
          <div v-for="agent in thirdSection.agents">
            <p>{{ agent }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { useSuggestionFilterViewModel } from "./useSuggestionFilterViewModel";

export default {
  props: {
    datasetQuestions: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      secondSection: [],
      thirdSection: null,
    };
  },
  methods: {
    changeToSecondSection(question) {
      this.secondSection = question.configurations;
    },
    changeToThirdSection(config) {
      this.thirdSection = config;
    },
  },
  setup(props) {
    return useSuggestionFilterViewModel(props);
  },
};
</script>
