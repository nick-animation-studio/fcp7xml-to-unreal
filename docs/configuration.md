# Configuration

**fcp7xml-to-unreal** reads configuration options from a YAML file. A [default configuration file](../src/premiere_to_ue/config.yaml) is provided with the product. If a file named `config.yaml` exists in the current directory, it will take precedence. The utility reports to the console about where configuration is read from.

## Default Config File

```yaml
audio:
  music_track_prefix: "Music"
  sfx_track_prefix: "SFX"
  track_colors:
    brown: "Scratch VO"
    yellow: "From Audio Library"
  track_color_nomatch_label: "Temp Material"

shot_name_regex: '[\d]{3}_[a-zA-Z0-9]+_shot_[\w]+.[a-zA-Z0-9]+'
```

shot_name_regex - regex that will be used to match the `name` of clipitems in the XML. The default regex above parses Shot naming as follows:

101_01_shot_001.mov: Episode '101', Scene '01', Shot '001', .mov extension
