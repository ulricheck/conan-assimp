from conans import ConanFile, CMake, tools
from conans.tools import download, unzip, replace_in_file, patch
import os


class AssimpConan(ConanFile):
    name = "assimp"
    version = "4.1.0"
    license = "MIT"
    url = "https://github.com/ulricheck/conan-assimp"
    description = "Conan package for Assmip"
    requires = (
        "zlib/[>=1.2.11]@camposs/stable", 
        )
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    exports = ["patches/*",]

    def source(self):
        zip_name = "v%s.zip" % self.version
        download("https://github.com/assimp/assimp/archive/%s" % zip_name, zip_name, verify=False)
        unzip(zip_name)
        os.unlink(zip_name)
        os.rename("assimp-%s" % self.version, "source")

        # if self.settings.os == "Windows" and self.settings.build_type=="Debug":
        #     #patch assimp to correctly build debug libraries on windows
        #     self.output.info("Apply patch: patch_windows_debug_build.diff")
        #     patch(base_path="source", 
        #         patch_file=os.path.join("patches", "patch_windows_debug_build.diff"), 
        #         strip=1)


        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file("source/CMakeLists.txt", "PROJECT( Assimp )", '''PROJECT( Assimp )
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')


    def build(self):
        cmake = CMake(self)

        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["ASSIMP_BUILD_TESTS"] = False
        cmake.definitions["ASSIMP_BUILD_SAMPLES"] = False
        # pdb file installation fails on msvc
        cmake.definitions["ASSIMP_INSTALL_PDB"] = False
        cmake.definitions["CMAKE_CXX_FLAGS"] = "-fPIC"
        cmake.definitions["CMAKE_C_FLAGS"] = "-fPIC"
        cmake.configure(source_dir="source")
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("*.h", dst="include", src="source/include")
        self.copy("*.hpp", dst="include", src="source/include")
        self.copy("*.inl", dst="include", src="source/include")
        self.copy("*assimp*.lib", dst="lib", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        if self.settings.os == "Windows":
            self.copy("*.dll", dst="bin", keep_path=False)
        if self.settings.os == "Macos":           
            self.copy("*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        is_apple = (self.settings.os == 'Macos' or self.settings.os == 'iOS')
        # if self.settings.build_type == "Debug" and not is_apple:
        #     self.cpp_info.libs = [lib+'d' for lib in self.cpp_info.libs]
        
        if self.settings.os == "Windows":
            self.cpp_info.cppflags.append("/EHsc")
        else:
            self.cpp_info.cppflags.append("-std=c++11")

        if self.settings.os == "Macos":
            self.cpp_info.cppflags.append("-stdlib=libc++")
