export const stringToColor = (string, saturation = 80, lightness = 80) => {
  let stringUniqueHash = [...string].reduce((acc, char) => {
    return char.charCodeAt(0) + ((acc << 5) - acc);
  }, 0);
  return `hsl(${stringUniqueHash % 360}, ${saturation}%, ${lightness}%)`;
};
