<template>
  <div class="datasets-empty">
    <svgicon
      class="datasets-empty__icon"
      width="44"
      height="46"
      name="unavailable"
    />
    <p class="datasets-empty__title">There aren't any datasets yet</p>
    <p class="datasets-empty__subtitle">
      The Argilla web app allows you to log, explore and annotate your data.<br />
      Start logging data with our Python client, or
      <a href="https://docs.rubrix.ml/" target="_blank">see the docs</a> for
      more information.
    </p>
    <base-code :code="generateCodeSnippet()"></base-code>
  </div>
</template>

<script>
import "assets/icons/unavailable";
export default {
  props: {
    workspace: {
      required: true,
      type: String,
    },
  },

  methods: {
    generateCodeSnippet() {
      return `# install datasets library with pip install datasets
import argilla as rg
from datasets import load_dataset

# load dataset from the hub
dataset = load_dataset("argilla/gutenberg_spacy-ner", split="train")

# read in dataset, assuming its a dataset for token classification
dataset_rg = rg.read_datasets(dataset, task="TokenClassification")

# log the dataset
rg.log(dataset_rg, "gutenberg_spacy-ner")`;
    },
  },
};
</script>
<style lang="scss" scoped>
.datasets-empty {
  text-align: center;
  margin: auto;
  margin-top: 12%;
  color: $black-54;
  max-width: 610px;
  line-height: 20px;
  &__icon {
    margin-bottom: 1em;
  }
  &__title {
    margin: 0 auto 1em auto;
    @include font-size(20px);
    font-weight: 300;
    max-width: 520px;
  }
  &__subtitle {
    margin: 0 auto 1em auto;
    @include font-size(14px);
    max-width: 520px;
    a {
      color: $brand-primary-color;
      text-decoration: none;
      &:hover {
        color: darken($brand-primary-color, 10%);
      }
    }
  }
}
</style>
