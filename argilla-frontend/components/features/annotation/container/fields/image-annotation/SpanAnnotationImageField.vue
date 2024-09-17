<template>
  <div style="position: relative" id="span-image-field-container">
    <canvas id="canvas" width="800" height="600"></canvas>
  </div>
</template>
<script>
import { useSpanAnnotationImageField } from "./useSpanAnnotationImageField";

export default {
  props: {
    spanQuestion: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    return useSpanAnnotationImageField({
      imageURL:
        "https://www.adslzone.net/app/uploads-adslzone.net/2021/03/Fotografo-haciendo-foto.jpg",
      ...props,
    });
  },
};
</script>

<style lang="scss">
#span-image-field-container {
  overflow: scroll;
}
#canvas {
  position: relative;
  max-width: none;
}
.delete-btn {
  position: absolute;
  background-color: red;
  color: white;
  border: none;
  cursor: pointer;
  width: 20px;
  height: 20px;
  text-align: center;
  line-height: 20px;
  font-size: 12px;
}
.annotation-text {
  position: absolute;
  background-color: white;
  padding: 5px;
  border: 1px solid black;
}
</style>
