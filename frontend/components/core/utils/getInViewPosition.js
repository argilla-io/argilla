const margin = 0;

const isAboveOfViewport = (element, position) =>
  position.top <= margin - parseInt(getComputedStyle(element).marginTop, 10);

const isBelowOfViewport = (element, position) =>
  position.top + element.offsetHeight + margin >=
  window.innerHeight - parseInt(getComputedStyle(element).marginTop, 10);

const isOnTheLeftOfViewport = (element, position) =>
  position.left <= margin - parseInt(getComputedStyle(element).marginLeft, 10);

const isOnTheRightOfViewport = (element, position) =>
  position.left + element.offsetWidth + margin >=
  window.innerWidth - parseInt(getComputedStyle(element).marginLeft, 10);

const getInViewPosition = (element, position) => {
  const computedStyle = getComputedStyle(element);

  if (isAboveOfViewport(element, position)) {
    position.top = margin - parseInt(computedStyle.marginTop, 10);
  }

  if (isOnTheLeftOfViewport(element, position)) {
    position.left = margin - parseInt(computedStyle.marginLeft, 10);
  }

  if (isOnTheRightOfViewport(element, position)) {
    position.left =
      window.innerWidth -
      margin -
      element.offsetWidth -
      parseInt(computedStyle.marginLeft, 10);
  }

  if (isBelowOfViewport(element, position)) {
    position.top =
      window.innerHeight -
      margin -
      element.offsetHeight -
      parseInt(computedStyle.marginTop, 10);
  }

  return position;
};

export default getInViewPosition;
