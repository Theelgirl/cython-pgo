# PGO and Related GCC Optimizations With Cython
## Summary
These are the options that I use when compiling my Cython files. I generally compile for execution speed, not code size, however I included comments explaining what each option does, so you can remove options locally if you want.
PGO stands for profile-guided-optimization, and I've experienced a noticeable speedup when using it properly in my code. It seems (at least to me) to work best when there's a large disparity in time taken between multiple parts of the program.

## Usage Instructions
1. Copy/paste my setup.py file into your cython directory
2. Run ``python3 setup.py build_ext --inplace`` in your terminal to compile the code. Everything except PGO will be active on this first run. **Important: You MUST use ``--inplace`` for PGO to work on later steps, otherwise the profiling data may be in a different place from where this expects it.**
3. Run the program once or twice, to generate the profiling data. Try to make sure at least some code from every file is executed on the runs, but it's fine if some files aren't executed.
4. Run ``python3 setup.py build_ext --inplace`` again, to allow compilation with the data gained from the previous runs.
5. Run the program!

Optional: If you think step 3 wasn't representative of real conditions and you've already passed it, go down into the build/ directory and delete the .gcda files, and start again from step 2.

## Recommendations/Notes
1. Use gcc 10.1+ or 11, as those seem to have much better PGO optimizations: [Clear Linux blog post about GCC 10.1 improvements](https://clearlinux.org/blogs-news/major-improvements-gcc-101)
2. Run this on Linux. It has not been tested on Windows, MacOS or any BSD systems. If you find that it works on any of those platforms, file an issue and I'll update this. If you'd like to make it work for any other OS, submit a PR.
3. This should work with either C or C++ code, but it has only been tested with C++ code.

## Benchmarks
I don't really know how to profile C/C++ code well, but if you can run benchmarks, please do, and submit them here!
