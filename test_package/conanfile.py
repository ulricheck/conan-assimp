from conans import ConanFile, CMake
import os

class AssimpTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "assimp/4.1.0@camposs/stable", "zlib/1.3.11@camposs/stable"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is in "test_package"
        cmake.configure(source_dir=self.conanfile_directory, build_dir="./")
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")

    def test(self):
       self.run(os.sep.join(["cd bin && .", "example"]))
