from setuptools import setup, Extension, find_packages

setup(
    name="ggj2024",
    install_requires= ["pygame", "numpy"],
    url="https://github.com/SpieleentwicklungBodensee/ggj_2024",
    license="MIT",
    #packages=["ggj2024"],
    ext_modules = [
        Extension(
            "Fluid",
            sources=["Fluid.pyx"],
        ),
    ],
    #package_data = {
    #    "ggj2024": ["gfx/*"]
    #},
)