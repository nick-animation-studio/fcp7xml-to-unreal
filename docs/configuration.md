# Configuration

**fcp7xml-to-unreal** reads configuration options from a YAML file. A default [config.yaml](https://github.com/nick-animation-studio/fcp7xml-to-unreal/blob/main/src/fcp7xml_to_unreal/config.yaml) is provided, but if a file named `config.yaml` exists in the current directory, it will take precedence. The utility reports to the console about where configuration is read from.

## Default Config File

```yaml
audio:
  music_track_prefix: "Music"
  sfx_track_prefix: "SFX"
  track_colors:
    brown: "Scratch VO"
    yellow: "From Audio Library"
  track_color_nomatch_label: "Temp Material"

frame_rate: '24'
shot_name_regex: '[\d]{3}_[a-zA-Z0-9]+_shot_[\w]+.[a-zA-Z0-9]+'
shot_name_resubs: [
  { 'pattern': r'\(.*\)', 'replacement': r'' },
  { 'pattern': r'_SB', 'replacement': r'' },
  { 'pattern': r"\_\d\d\d\d\d\d\d\d", 'replacement': r''},
  ]

MOVIE_FILE_SUFFIXES: {'mov'}
IMAGE_FILE_SUFFIXES: {"png", "jpg"}

# Here are the values for the provided burnins
CONFORMSHOT_BURNIN_PREFIX: "shot_"
CONFORMSCENE_BURNIN_PREFIX: "scene_"

# Here are the values for the Premiere test .xml file
# CONFORMSHOT_BURNIN_PREFIX: "Sc_"
# CONFORMSCENE_BURNIN_PREFIX: "seq"
```

`shot_name_regex` - regex that will be used to match the `name` of clipitems in the XML. The default regex above parses Shot naming as follows:

101_01_shot_001.mov: Show '101', Scene '01', Shot '001', '.mov' extension

`shot_name_resubs` - regexes applied to the `name` of clipitems in the XML. The default regexes above act as follows:

- remove suffixes like "(abc)" and "(temp)" from the end of the name of shots, if present.
- remove "_SB" from the end of the name of shots, if present.
- remove date strings like "_20241201" from the end of the name of shots, if present.
