# How to Convert Time Reports

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin time convert` reference section](../../reference/cli/time.md#compiler-admin-time-convert).

This guide explains how to use the `compiler-admin time convert` command to convert a time report from one format (like Toggl) to another (like Harvest or Justworks).

## Basic Usage

The `convert` command reads from an input source, which defaults to `toggl` format, and writes to an output source, which defaults to `harvest` format.

The simplest usage reads from standard input and writes to standard output:

```bash
cat toggl-report.csv | compiler-admin time convert > harvest-report.csv
```

## Specifying Input and Output Files

For clarity, it's often better to use the `--input` and `--output` flags.

```bash
compiler-admin time convert --input toggl-report.csv --output harvest-report.csv
```

## Specifying Conversion Formats

You can explicitly define the source and destination formats using the `--from` and `--to` flags.

### Convert from Toggl to Harvest

```bash
compiler-admin time convert \
  --from toggl \
  --to harvest \
  --input toggl-export.csv \
  --output harvest-import.csv
```

### Convert from Harvest to Toggl

```bash
compiler-admin time convert \
  --from harvest \
  --to toggl \
  --input harvest-export.csv \
  --output toggl-import.csv
```

### Convert from Toggl to Justworks

```bash
compiler-admin time convert \
  --from toggl \
  --to justworks \
  --input toggl-export.csv \
  --output justworks-import.csv
```

## Setting a Client Name

When converting, you may need to specify a client name for the destination format. Use the `--client` option for this.

```bash
compiler-admin time convert \
  --input toggl.csv \
  --output harvest.csv \
  --client "Specific Client Name"
```
