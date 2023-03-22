import Vue from "vue";

Vue.directive("circle", {
  bind: (element) => {
    element.style.display = "flex";
    element.style.alignItems = "center";
    element.style.justifyContent = "center";
    element.style.backgroundColor = "#ff675f";
    element.style.color = "white";
    element.style.height = "34px";
    element.style.width = "34px";
    element.style.borderRadius = "50%";
    element.style.fontSize = "1rem";
    element.style.fontWeight = "500";
    element.style.lineHeight = "34px";
    element.style.textTransform = "uppercase";
  },
});
