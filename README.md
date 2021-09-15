# Plopper

    Write a uniform distribution of files to disk for testing/benchmarking purposes
    [Public Repo](https://github.com/mieweb/ploppler) [MIE's internal repo](https://github.com/mieweb/plopper)

# CLI Usage
    Plops out a random distribution of files to the filesystem
    usage: plopper.py [--help] [-l MIN] [-h MAX] [-f FILES] [-t THREADS]
                      [--skeleton] [-m MASK] [-o OUTPUT] [-r ROOT]

    optional arguments:
      --help                show this help message and exit
      -l MIN, --min MIN     Minimum file size (bytes or appropriate unit; 1K, 2M)
      -h MAX, --max MAX     Maximum file size (bytes or appropriate unit; 1K, 2M)
      -f FILES, --files FILES
                            Number of files to generate
      -t THREADS, --threads THREADS
                            Number of threads to spawn (defaults to OS cpu_count)
      --skeleton            Only create the file skeleton of size without writing
                            any data
      -m MASK, --mask MASK  Create a subdirectory structure of each file based on
                            it's name. Mask should use an x character to denote a
                            digit of the filename. The default of no mask puts
                            each file as a uniquely named file in a single output
                            directory
      -o OUTPUT, --output OUTPUT
                            Output path to write files to
      -r ROOT, --root ROOT  Root directory name containing any masked
                            subdirectories

# Examples:

    # Write 500 files from 1M to 10M into the /var/log directory
    ./plopper.py --files 500 --min 1M --max 10M --output /var/log

    # Write 1,000,000 files from 1K to 1G into your home directory with a numerical mask for subdirectories
    ./plopper.py --files 1000000 --min 1K --max 1G --output ~ --root plopperHomeFiles --mask xxx/xxx/xxx
    # This will write files to ~/plopperHomeFiles/000/000/001, 002, etc...

    # If your mask isn't large enough to hold the number of files without overwriting previous files,
    # the mask will be automatically prepended with additional padding
    ./plopper.py --files 15 --mask x
    # Mask is auto-converted to x/x

