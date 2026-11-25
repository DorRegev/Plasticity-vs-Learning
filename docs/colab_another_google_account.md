# Running the notebooks from another Google account, reusing saved results

Notebooks `02`–`08` save everything slow to compute in one Google Drive folder:
`/content/drive/MyDrive/plasticity_lens_cache`. This includes the tuned lens, lens results, head scores and switch-off
results. Another Google account (for example, one that still has free Colab GPU time) can reuse those results.
**The notebooks need no change:** they look for a folder with that exact name at the top of My Drive. A shortcut to
your original folder counts as that folder.

## In your current account (the one with the results)
1. Open [drive.google.com](https://drive.google.com), right-click the `plasticity_lens_cache` folder, and choose
   **Share**.
2. Add the new account's email as an **Editor**. Editor access matters because the notebooks also save new results
   into this folder.

## In the new account
1. Open [drive.google.com](https://drive.google.com) and go to **Shared with me**.
2. Right-click `plasticity_lens_cache` → **Organize → Add shortcut** → choose **My Drive** (the top level, not a
   subfolder).
   - Keep the name exactly `plasticity_lens_cache`.
   - If the new account already has a folder with that name, rename or delete it first.
3. Add your Hugging Face token, which the gated Mistral model needs. The token belongs to your Hugging Face account, so
   the same one works.
   - In Colab, click the **key icon** in the left sidebar → **Add new secret**.
   - Name it `HF_TOKEN`, paste the token, and turn on **Notebook access**.
4. Open the notebook from GitHub as usual (its README has an "Open in Colab" link), select a T4 GPU
   (**Runtime → Change runtime type**), and choose **Runtime → Run all**.
   - When the Drive popup appears, sign in with the **new** account.

## Check before the long run
After the first cell (the Drive mount), add a code cell and run:

```
!ls /content/drive/MyDrive/plasticity_lens_cache
```

It should list folders like `head_specialization`, `induction_heads`, `transition_memory` and `metric_validation`.
In the output, look for lines like `loaded 20 runs … from /content/drive/MyDrive/plasticity_lens_cache/…`. Those
confirm the old results are being reused rather than recomputed.

## Two notes
- Files the new account saves into the shared folder count against your **original** account's storage, because that
  account owns the folder.
- Colab's terms prohibit using multiple accounts to get around its usage limits. Check them before relying on this.
