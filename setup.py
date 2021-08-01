import os
import sys
from distutils.core import Extension, setup

from Cython.Build import cythonize

# these two replaces could be considered wasteful but i couldn't think of a simpler option
# if you have an idea on how to improve, please submit a pr

def use_profiling():
    os.environ["CFLAGS"] = os.environ["CFLAGS"].replace("-fprofile-generate", "")
    os.environ["CFLAGS"] = os.environ["CFLAGS"].replace("-fprofile-use -fprofile-correction", "")
    os.environ["CFLAGS"] += "-fprofile-use -fprofile-correction"


def generate_profiling():
    os.environ["CFLAGS"] = os.environ["CFLAGS"].replace("-fprofile-generate", "")
    os.environ["CFLAGS"] = os.environ["CFLAGS"].replace("-fprofile-use -fprofile-correction", "")
    os.environ["CFLAGS"] += "-fprofile-generate"


def run_setup(force=False):
    setup(
        ext_modules=cythonize(
            Extension(
                name="*",
                sources=["*.pyx"],
            ),
            # feel free to remove annotate and compiler_directives in your own version
            annotate=True,
            compiler_directives={"language_level": 3, "infer_types": True},
            force=force,
        )
    )


if __name__ == "__main__":

    # set our compilation flags
    # march=native to enable SIMD optimizations based on our cpu
    # LTO docs: https://gcc.gnu.org/onlinedocs/gcc-11.1.0/gcc/Optimize-Options.html#index-flto
    # DO NOT USE -fwhole-program
    # tree-vectorize helps with SIMD stuff
    # no-semantic-interposition is more useful for code that exports a ton of symbols, but I include it anyway:
    # https://stackoverflow.com/questions/35745543/new-option-in-gcc-5-3-fno-semantic-interposition
    # profile-partial-training stops gcc from assuming that functions not in the gcda data are never executed
    # feel free to remove profile-partial-training if it helps you
    # pipe makes compilation faster on supported systems, reference here:
    # https://gcc.gnu.org/onlinedocs/gcc-11.1.0/gcc/Overall-Options.html#index-pipe
    os.environ[
        "CFLAGS"
    ] = "-march='native' -flto -ftree-vectorize -fno-semantic-interposition -fprofile-partial-training -pipe "

    gcda_exists = set()

    for dirpath, _, files in os.walk("./"):
        for filename in files:
            if filename.endswith(".gcda"):
                # slice the '.gcda' off
                gcda_exists.add(filename[:-5])

    for module_name in FILES_TO_COMPILE:
        # set a backup of sys.stdout so we have something to go back to
        stdout = sys.stdout
        generate_profiling()
        # redirect stdout into a file so we can parse the output
        with open("temp.txt", "w+") as sys.stdout:
            run_setup(force=False)
        # return stdout to normal
        sys.stdout = stdout
        with open("temp.txt", "r+") as tmpfile:
            # strip to remove trailing \n
            content = tmpfile.read().strip()
            # let the user know the file has been processed instead of being silent
            print(content)
            # if the file hasn't been changed since the previous compilation, we likely have a gcda file to profile with
            # and if there's already an existing gcda file, then we *know* that there has been profiling going on
            if content == "running build_ext" and module_name in gcda_exists:
                use_profiling()
                # force a recompile that uses the pgo data
                run_setup(force=True)
