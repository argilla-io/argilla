<template>
  <div class="datasets-empty">
    <svgicon
      class="datasets-empty__icon"
      width="44"
      height="46"
      name="datasets-empty"
    />
    <p class="datasets-empty__title">There aren't any datasets yet</p>
    <p class="datasets-empty__subtitle">
      The Rubrix web app allows you to log, explore and annotate your data.<br />
      Start logging data with our Python client, or
      <a href="https://docs.rubrix.ml/" target="_blank">see the docs</a> for
      more information.
    </p>
    <re-code :code="generateCodeSnippet(workspace)"></re-code>
  </div>
</template>

<script>
import "assets/icons/datasets-empty";
export default {
  props: {
    workspace: {
      required: true,
      type: String,
    },
  },

  methods: {
    generateCodeSnippet(ws) {
      return `import rubrix as rb

# If you are using the default installation you can skip this line
rb.set_workspace("${ws}")

rb.log(
  rb.TextClassificationRecord(inputs="my first rubrix example"), 
  name='example-dataset'
)`;
    },
  },
};
</script>
<style lang="scss" scoped>
.datasets-empty {
  text-align: center;
  margin: auto;
  margin-top: 12%;
  color: palette(grey, medium);
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
      color: $primary-color;
      text-decoration: none;
      &:hover {
        color: darken($primary-color, 10%);
      }
    }
  }
}
</style>
