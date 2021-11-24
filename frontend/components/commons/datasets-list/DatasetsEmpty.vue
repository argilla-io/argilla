<template>
  <div class="datasets-empty">
    <svgicon class="datasets-empty__icon" width="36" height="36" name="datasets-empty" />
    <p class="datasets-empty__title">There aren't any datasets yet</p>
    <p class="datasets-empty__subtitle">The Rubrix web app allows you to log, explore and annotate your data.
Start logging data with our Python client, or <a href="https://docs.rubrix.ml/" target="_blank">see the docs</a> for more information.</p>
    <re-code>import rubrix as rb

rb.log(
  rb.TextClassificationRecord(inputs={"text": "my first rubrix example"}),
  name='example-dataset'
)</re-code>
  </div>
</template>

<script>
import "assets/icons/datasets-empty";
export default {};
</script>
<style lang="scss" scoped>
.datasets-empty {
  text-align: center;
  margin: auto;
  max-width: 460px;
  margin-top: 15%;
  color: palette(grey, medium);
  &__icon {
    margin-bottom: 1em;
  }
  &__title {
    margin-bottom: 1em;
    margin-top: 0;
    @include font-size(18px);
    font-weight: 300;
  }
  &__subtitle {
    margin-bottom: 1em;
    margin-top: 0;
    @include font-size(13px);
    font-weight: 300;
    a {
      color: $primary-color;
      text-decoration: none;
      &:hover {
        color: darken($primary-color, 10%)
      }
    }
  }
}
.highlight {
  background-color: #333346;
  color: white;
  padding: 1em !important;
}
</style>

