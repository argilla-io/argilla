<template>
  <HeaderAndTopAndOneColumn>
    <template v-slot:header>
      <HeaderComponent />
    </template>
    <template v-slot:center
      ><div class="container">
        <div class="daboudi"></div>
        <QuestionsFormComponent :initialInputs="inputs" />
      </div>
    </template>
  </HeaderAndTopAndOneColumn>
</template>

<script>
import HeaderAndTopAndOneColumn from "@/layouts/HeaderAndTopAndOneColumn";

export default {
  name: "DatasetPage",
  components: {
    HeaderAndTopAndOneColumn,
  },
  created() {
    this.inputs = [
      // {
      //   id: "id_1",
      //   question:
      //     "Are the instruction and input adequate for the capabilities of this model?",
      //   outputs: [
      //     { id: 1, value: true, text: "Yes" },
      //     { id: 2, value: false, text: "No" },
      //   ],
      //   default: null,
      //   required: true,
      //   componentType: "SINGLE_LABEL",
      // },
      // {
      //   id: "id_2",
      //   question: "Does the output contain hallucinated or untruthful facts?",
      //   outputs: [
      //     { id: 1, value: true, text: "Yes" },
      //     { id: 2, value: false, text: "No" },
      //   ],
      //   default: null,
      //   componentType: "SINGLE_LABEL",
      // },
      // {
      //   id: "id_3",
      //   question:
      //     "Select any labels that apply to the content found in the text:",
      //   outputs: [
      //     { id: 1, text: "Not English", label: "Not English" },
      //     { id: 2, text: "Not Appropriate", label: "Not Appropriate" },
      //     { id: 3, text: "Contains PII", label: "Contains PII" },
      //     { id: 4, text: "Hate Speech", label: "Hate Speech" },
      //     { id: 5, text: "Sexual Content", label: "Sexual Content" },
      //     { id: 6, text: "Daboudi", label: "Daboudi" },
      //     { id: 7, text: "Dabouda", label: "Dabouda" },
      //     { id: 8, text: "Patati", label: "Patati" },
      //     { id: 9, text: "Patata", label: "Patata" },
      //     { id: 10, text: "baguette", label: "baguette" },
      //     { id: 11, text: "pain au chocolat", label: "pain au chocolat" },
      //     { id: 12, text: "croissant", label: "croissant" },
      //   ],
      //   default: null,
      //   componentType: "SINGLE_LABEL",
      // },
      // {
      //   id: "id_4",
      //   question: "Rate the overall quality of the output",
      //   outputs: [
      //     { id: 1, value: 1, text: "1" },
      //     { id: 2, value: 2, text: "2" },
      //     { id: 3, value: 3, text: "3" },
      //     { id: 4, value: 4, text: "4" },
      //     { id: 5, value: 5, text: "5" },
      //   ],
      //   default: null,
      //   componentType: "SINGLE_LABEL",
      // },
      {
        id: "id_5",
        question:
          "Rate the helpfulness of the output (1-not helpful, 5-very helpful):",
        outputs: [
          { id: 1, value: true, text: "1" },
          { id: 2, value: false, text: "2" },
          { id: 3, value: false, text: "3" },
          { id: 4, value: false, text: "4" },
          { id: 5, value: false, text: "5" },
          { id: 6, value: false, text: "6" },
          { id: 7, value: false, text: "7" },
        ],
        required: true,
        componentType: "RATING",
      },
      {
        id: "id_6",
        question:
          "Rate the harmlessness of the output (1-very harmful, 5-harmless):",
        outputs: [
          { id: "id_6-1", value: false, text: "1" },
          { id: "id_6-2", value: false, text: "2" },
          { id: "id_6-3", value: false, text: "3" },
          { id: "id_6-4", value: false, text: "4" },
          { id: "id_6-5", value: true, text: "5" },
        ],
        required: false,
        tooltipMessage: "This is a tooltipz",
        componentType: "RATING",
      },
      {
        id: "id_7",
        question: "Comment",
        outputs: { text: "dadadadda", placeholder: "this is the placeholder" },
        default: null,
        required: false,
        tooltipMessage: "This is a tooltip",
        componentType: "FREE_TEXT",
      },
    ];
  },
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
}
.daboudi {
  flex: 1;
  background: red;
}
</style>
