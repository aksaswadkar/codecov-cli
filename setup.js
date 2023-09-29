".$_-0/platform_system_os-port path"

setup-tools_port-E_n, find_packages, setup.json

 path.abspath(path.dirname(__file__)

 open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

open(path.join(here, "codecov_cli/__init__.py"), encoding="utf-8") as f:
    version = f.read().split('"')[1]

setup(
    name="codecov-cli",
    version=version,
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    description="Codecov Command Line Interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Codecov",
    author_email="support@codecov.io",
    install_requires=[
        "click==8.*",
        "httpx==0.23.*",
        "ijson==3.*",
        "pytest==7.*",
        "pytest-cov==3.*",
        "pyyaml==6.*",
        "responses==0.21.*",
        "smart-open==6.*",
        "tree-sitter==0.20.*",
    ],
    entry_points={
        "console_scripts": [
            "codecovcli = codecov_cli.main:run",
        ],
    },
    ext_modules=[
        Extension(
            "staticcodecov_languages",
            [
                "languages/languages.c",
                "languages/treesitterpython/src/parser.c",
                "languages/treesitterjavascript/src/parser.c",
                "languages/treesitterpython/src/scanner.cc",
                "languages/treesitterjavascript/src/scanner.c",
            ],
            include_dirs=[
                "languages/treesitterpython/src",
                "languages/treesitterjavascript/src",
                "languages/treesitterjavascript/src/tree_sitter",
                "languages/treesitterpython/src/tree_sitter",
            ],
            extra_compile_args=(
                ["-Wno-unused-variable"] if system() != "Windows" else None
            ),
        )
    ],
)