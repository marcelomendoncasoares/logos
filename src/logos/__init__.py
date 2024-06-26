"""
Logos package entrypoint.
"""

import os


# Prevents the following error on Windows, although not recommended by Intel:
#
# OMP: Error #15: Initializing libomp140.x86_64.dll, but found libiomp5md.dll
# already initialized.
#
# OMP: Hint This means that multiple copies of the OpenMP runtime have been
# linked into the program. That is dangerous, since it can degrade performance
# or cause incorrect results. The best thing to do is to ensure that only a
# single OpenMP runtime is linked into the process, e.g. by avoiding static
# linking of the OpenMP runtime in any library. As an unsafe, unsupported,
# undocumented workaround you can set the environment variable KMP_DUPLICATE_LIB_OK=TRUE
# to allow the program to continue to execute, but that may cause crashes or
# silently produce incorrect results. For more information, please see
# http://openmp.llvm.org/
#
# The conflict seems to be caused by Faiss, that tries to load the libomp140.x86_64.dll
# library, while the Intel OpenMP runtime has already been initialized by PyTorch.
#
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
