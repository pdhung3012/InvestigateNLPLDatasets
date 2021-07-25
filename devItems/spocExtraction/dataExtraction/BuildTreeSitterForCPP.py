import glob
import sys, os
import operator

from tree_sitter import Language, Parser
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('../../')))
from UtilFunctions import createDirIfNotExist,getPOSInfo,writeDictToFileText


fopData='/home/hungphd/'
fopGithub='/home/hungphd/git/'
fopBuildFolder=fopData+'build-tree-sitter/'
createDirIfNotExist(fopBuildFolder)

fpLanguageSo=fopBuildFolder+'my-languages.so'
fpTreeSitterC=fopGithub+'tree-sitter-c'
fpTreeSitterCPP=fopGithub+'tree-sitter-cpp'

# Language.build_library(
#   # Store the library in the `build` directory
#   fpLanguageSo,
#
#   # Include one or more languages
#   [
#     fpTreeSitterC,
#     fpTreeSitterCPP
#   ]
# )
Language.build_library(
  # Store the library in the `build` directory
  fopBuildFolder+'/my-languages.so',

  # Include one or more languages
  [
    fopGithub+'/tree-sitter-go',
    fopGithub+'/tree-sitter-javascript',
    fopGithub+'/tree-sitter-python',
    fopGithub+'/tree-sitter-c',
    fopGithub+'/tree-sitter-cpp'
  ]
)