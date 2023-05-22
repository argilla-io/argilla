import { shallowMount } from "@vue/test-utils";
import EditableDescriptionMarkdown from "./EditableDescriptionMarkdown.component.vue";

const options = {
    propsData: {
        description: "FAKE_DESCRIPTION"
    },
};

jest.mock("marked", () => {
    return {
        marked: {
            parse: jest.fn((value) => `${value}-PARSED`)
        }
    }
})

describe("EditableDescriptionMarkdown should", () => {
    it("make editable when user clicks on pencil", async () => {
        const wrapper = shallowMount(EditableDescriptionMarkdown, options);
        await wrapper.find("[name=edit-button]").trigger("on-click");

        expect(wrapper.vm.$data.isEditing).toBe(true)
    })

    it("make no editable when user clicks on discard", async () => {
        const wrapper = shallowMount(EditableDescriptionMarkdown, options);
        await wrapper.find("[name=edit-button]").trigger("on-click");

        await wrapper.find("[name=close-button]").trigger("on-click");

        expect(wrapper.vm.$data.isEditing).toBe(false)
    })

    it("raise onSave event when user clicks on save button", async () => {
        const wrapper = shallowMount(EditableDescriptionMarkdown, options);
        await wrapper.find("[name=edit-button]").trigger("on-click");

        await wrapper.find("[name=save-button]").trigger("on-click");

        expect(wrapper.vm.$data.isEditing).toBe(false)
        expect(wrapper.emitted().onSave).toEqual([["FAKE_DESCRIPTION"]])
    })
})