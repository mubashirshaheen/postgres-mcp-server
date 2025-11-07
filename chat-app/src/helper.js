
const getRandomColor = () => {
  var letters = "0123456789ABCDEF";
  var color = "#";
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 10)];
  }
  return color;
};
const colorsArray = (index) => {
  const COLORS = [
    "#436A9F",
    "#2DFFF6",
    "#FF6633",
    "#43425D",
    "#4D4F5C",
    "#B34D4D",
    "#636363",
    "#79BCA0",
    "#66991A",
    "#FFFF99",
    "#3366E6",
    "#4D8000",
    "#FFB399",
    "#FFFF99",
    "#00B3E6",
    "#A8B8D4",
    "#00EFD4",
    "#7AD236",
    "#7260D8",
    "#1DEAA7",
    "#823C59",
    "#E3D94C",
    "#DC1C06",
    "#F53B2A",
    "#B46238",
    "#1A8011",
    "#1A806A",
    "#4CF09D",
    "#C188A2",
    "#67EB4B",
    "#B308D3",
    "#FC7E41",
    "#AF3101",
    "#ff065",
    "#71B1F4",
    "#A2F8A5",
    "#E23DD0",
    "#D3486D",
    "#00F7F9",
    "#474893",
    "#3CEC35",
    "#5D1D0C",
    "#2D7D2A",
    "#FF3420",
    "#5CDD87",
    "#A259A4",
    "#E4AC44",
    "#1BEDE6",
    "#8798A4",
    "#D7790F",
    "#B2C24F",
    "#DE73C2",
    "#D70A9C",
    "#25b67",
    "#88E9B8",
    "#C2B0E2",
    "#86E98F",
    "#AE90E2",
    "#1A806B",
    "#436A9E",
    "#0EC0FF",
    "#F812B3",
    "#B17FC9",
    "#8D6C2F",
    "#D3277A",
    "#2CA1AE",
    "#9685EB",
    "#8A96C6",
    "#DBA2E6",
    "#76FC1B",
  ];
  for (let i = 0; i < index; i++) {
    const randomColor = getRandomColor();
    COLORS.push(randomColor);
  }
  return COLORS;
};

export {
  colorsArray,
  getRandomColor,
};