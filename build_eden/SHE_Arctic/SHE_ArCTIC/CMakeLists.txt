CMAKE_MINIMUM_REQUIRED(VERSION 2.8.5)

#===============================================================================
# Load elements_subdir macro here
# Examples:
#   For declaring a project module:
#         elements_subdir(ElementsExamples)
#===============================================================================
elements_subdir(SHE_ArCTIC)

#===============================================================================
# Load elements_depends_on_subdirs macro here
#   For creating a dependency onto an other accessible module
#         elements_depends_on_subdirs(ElementsKernel)
#===============================================================================
elements_depends_on_subdirs(ElementsKernel)

find_package(NumPy)
find_package(GSL)

#===============================================================================
# Declare the library dependencies here
# Example:
#         elements_add_library(ElementsExamples src/Lib/*.cpp
#                     INCLUDE_DIRS Boost ElementsKernel
#                     LINK_LIBRARIES Boost ElementsKernel
#                     PUBLIC_HEADERS ElementsExamples)
#===============================================================================
elements_add_library(SHE_ArCTIC src/lib/*.cpp
                     INCLUDE_DIRS ElementsKernel SHE_ArCTIC GSL
                     LINK_LIBRARIES ElementsKernel GSL
                     PUBLIC_HEADERS SHE_ArCTIC)

#===============================================================================
# Add the find_package macro (a pure CMake command) here to locate the
# libraries.
# Examples:
#          find_package(CppUnit)
#===============================================================================
elements_add_cython_module(src/Cython/lib/SHE_ArCTIC_wrapper.pyx src/wrapper/interface.cpp
                           LINK_LIBRARIES Numpy SHE_ArCTIC GSL
                           INCLUDE_DIRS Numpy GSL
                           NO_PUBLIC_HEADERS)

#===============================================================================
# Declare the executables here
# Example:
# elements_add_executable(ElementsProgramExample src/Program/ProgramExample.cpp
#                        INCLUDE_DIRS Boost ElementsExamples
#                        LINK_LIBRARIES Boost ElementsExamples)
#===============================================================================

#===============================================================================
# Declare the Boost tests here
# Example:
# elements_add_unit_test(BoostClassExample tests/src/Boost/ClassExample_test.cpp
#                       EXECUTABLE BoostClassExample_test
#                       INCLUDE_DIRS ElementsExamples
#                       LINK_LIBRARIES ElementsExamples TYPE Boost)
#===============================================================================
#elements_add_unit_test(SHE_ArCTIC tests/src/SHE_Arc_test.cpp
#                     EXECUTABLE SHE_Arc_SHE_Arc_test
#                     LINK_LIBRARIES SHE_ArCTIC
#                     TYPE Boost)

# elements_add_unit_test(Boost_SHE_ArCTIC_ccd tests/src/test_ccd.cpp
#                      LINK_LIBRARIES SHE_ArCTIC TYPE Boost
#                     )

#===============================================================================
# Use the following macro for python modules, scripts and aux files:
#  elements_install_python_modules()
#  elements_install_scripts()
#===============================================================================

#===============================================================================
# Declare the Python programs here
# Examples :
# elements_add_python_program(PythonProgramExample
#                             ElementsExamples.PythonProgramExample)
#===============================================================================

#===============================================================================
# Add the elements_install_conf_files macro
# Examples:
#          elements_install_conf_files()
#===============================================================================
# elements_install_conf_files()