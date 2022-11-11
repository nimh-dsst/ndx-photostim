

# Creating API documentation

To generate documentation for the Python API, change your directory to the `api_documentation` folder (e.g., via `cd api_documentation` or something similar.)

Then, we create the documentation using Sphinx and a template from ReadTheDocs. To generate this documentation for yourself, 
run the following commands (while in the `api_documentation` folder):

```angular2svg
<!--sphinx-apidoc -o source ..-->
<!--sphinx-apidoc -o source ../src/pynwb-->
sphinx-build -b html api_docs/source/ api_docs/build/
```

This will generate HTML files in the `./build` directory of `api_documentation`. Select `./build/index.html` to access the documentation
in a website format.

