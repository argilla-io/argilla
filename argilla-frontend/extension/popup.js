/* eslint-disable no-undef */
async function saveSettings(settings) {
  const [activeTab] = await chrome.tabs.query({
    active: true,
    lastFocusedWindow: true,
  });
  await chrome.scripting.executeScript({
    target: { tabId: activeTab.id },
    function: (settings) => {
      localStorage.setItem("argilla-dev", JSON.stringify(settings)),
        location.reload();
    },
    args: [settings],
  });
}

async function getStorageSetting() {
  const [activeTab] = await chrome.tabs.query({
    active: true,
    lastFocusedWindow: true,
  });
  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId: activeTab.id },
    function: () => localStorage.getItem("argilla-dev"),
  });

  return result ? JSON.parse(result) : {};
}

async function submitHandler(event) {
  event.preventDefault();
  const form = event.target;
  const inputs = form.querySelectorAll("input");
  const settings = {};

  inputs.forEach((input) => {
    const { id, value } = input;
    settings[id] = value ?? 1000;
  });

  await saveSettings(settings);
}

async function run() {
  const settings = await getStorageSetting();
  const form = document.querySelector("form");
  form.addEventListener("submit", submitHandler);

  const inputs = document.querySelectorAll("form input");

  inputs.forEach((input) => {
    const { id } = input;
    const value = settings[id];
    input.value = value ?? 1000;
  });
}

run();
