import Vue from "vue";
Vue.directive("circle", {
  bind: (element, binding) => {
    let circleDiameter = "0px";

    const { size } = binding?.value ?? { size: "SMALL" };

    switch (size) {
      case "SMALL":
        circleDiameter = "34px";
        break;
      case "MEDIUM":
        circleDiameter = "45px";
        break;
      default:
        circleDiameter = "34px";
    }

    element.style.display = "flex";
    element.style.alignItems = "center";
    element.style.justifyContent = "center";
    element.style.height = circleDiameter;
    element.style.width = circleDiameter;
    element.style.borderRadius = "50%";
    element.style.border = "1px solid var(--bg-opacity-1)"
    element.style.fontSize = "1rem";
    element.style.fontWeight = "500";
    element.style.lineHeight = "34px";
    element.style.textTransform = "uppercase";
  },
});
