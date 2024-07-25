---
description: Configure Argilla on Hugging Face Spaces
---
By default Argilla Spaces are **configured with a Sign in with Hugging Face button**. This enables other users in the Hugging Face Hub to join your Space and collaborate on your projects.

If you **don't want anyone else to join your space or want full control to add users**: 

1. You can disable the HF OAuth, or
2. Make your Space Private.

If you want to restrict access to your Space to members of an specific Hugging Face organization:

!!! info "Creating a Space under your personal account" 
    If you are creating the Space under your personal account, **don't insert any value for `USERNAME` and `PASSWORD`**. Once you launch the Space you will be able to Sign in with your Hugging Face username and the `owner` role. 

!!! info "Creating a Space under an organization" 
    If you are creating the Space under an organization **make sure to insert your Hugging Face username in the secret `USERNAME`**. In this way, you'll be able to Sign in with your Hugging Face user.

### Space creation settings

#### Owner

By default, the Space will be created in under your personal account. 

If you are part of some Hugging Face organizations and have enough rights you will see them in the dropdown list. If you select an organization, the Space will be created under `https://huggingface.co/spaces/{organization_name}/`.

#### Space hardware

For most usages you can leave the default `CPU basic FREE` option. For usage with more than 50 annotators and large datasets, `CPU Upgrade PAID` is recommended.

#### Persistent Storage
By default, persistent storage is set to `Small PAID`, which is paid services, charged per hour of usage. This is the most important setting if you plan to use Argilla more than a few hours. 

If you just want to quickly test or use Argilla for a few hours with the risk of loosing your datasets, choose `Ephemeral FREE`. 

!!! warning "Ephemeral persistent storage"
    Not setting persistent storage to `Small` means that **you will loose your data when the Space restarts**. 

#### Space Secrets

By default Argilla Spaces are configured with a sign in with Hugging Face button. 

!!! info "Creating a Space under your personal account" 
    If you are creating the Space under your personal account, **don't insert any value for `USERNAME` and `PASSWORD`**. Once you launch the Space you will be able to Sign in with your Hugging Face username and the `owner` role. 

!!! info "Creating a Space under an organization" 
    If you are creating the Space under an organization **make sure to insert your Hugging Face username in the secret `USERNAME`**. In this way, you'll be able to Sign in with your Hugging Face user.

## Connect to a private Space with the SDK
 If you are using a private Hugging Face Space, you need to specify your `HF_TOKEN` which can be found [here](https://huggingface.co/settings/tokens).
 
```python
import argilla as rg

HF_TOKEN = "..."

client = rg.Argilla(
    api_url="<api_url>",
    api_key="<api_key>"
    headers={"Authorization": f"Bearer {HF_TOKEN}"}
)
```