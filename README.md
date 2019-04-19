# d2l-build

[Under developing]

## Build pipeline

![](./build.svg)

The source files are markdown files. They are either purely markdown files or
juypyter notebooks saved in the markdown format with output removed. For the
latter, we may use Jupyter to edit them directly with the `notedown` plugin and
then run "Kernel -> Restart & Clear Output" before committing.
