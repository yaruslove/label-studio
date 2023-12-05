## First you need convert LS to mask gray

you need to tweak config.yaml

```
python3 main.py
```

### Second convert grayscale annotations to pseudo-color annotations
```
python3 gray2pseudo_color.py <dir_or_file> <output_dir>

python3 gray2pseudo_color.py data/Annotations_gray data/Anot_pseudo_gray
```

