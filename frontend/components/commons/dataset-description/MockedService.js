import Vue from 'vue'

const FAKE_DESCRIPTION = `# Title 

## Subtitle`;

const fakeDataset = Vue.observable({
    description: FAKE_DESCRIPTION
})

export const getDatasetDescription = (datasetId, datasetTask) => {
    return fakeDataset.description;
}

export const saveDescription = (datasetId, datasetTask, newDescription) => {
    fakeDataset.description = newDescription;

    return Promise.resolve();
}