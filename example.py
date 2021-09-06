# %%

from runtime import load_config, execute, WorkUnit

cleansing_params, segmentation_params, mel_spec_params, colos_spec_params = load_config()

work = WorkUnit(
    source_file = 'samples/sound-error.ogg',
    cleansing_params = cleansing_params,
    segmentation_params = segmentation_params,
    mel_spec_params = mel_spec_params,
    color_spec_params = colos_spec_params,
)
# %%

output = execute(work)

# %%
for result in output:
    print(result)
# %%
