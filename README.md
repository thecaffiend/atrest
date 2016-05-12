# Atlassian REST API Testing Notebook
Repo for playing with the Atlassian REST APIs via Python.

### Dependencies
There is no requirements.txt for use with the conda environment yet. It will be
forthcoming. For now, here are the things:
* [Anaconda](https://www.continuum.io/why-anaconda) - For managing the Python3
  (3.5) environment and dependencies (Jupyter notebook, other pip packages,
  etc).
* IPython - Installed with Anaconda and absolutely required for all the Python
  things
* manual pip upgrade performed in the environment `pip install --upgrade pip`
* [PythonConfluenceAPI](https://github.com/pushrodtechnology/PythonConfluenceAPI)
  A Python wrapper for the REST API. Install (after activating the right
  environment) via pip `pip install --upgrade PythonConfluenceAPI`. As of the
  time of writing, this installs 0.0.1rc6 (latest without upgrade is 0.0.1rc4)
* future - `pip install 'future>=0.15.2,<1'` There is a specific version need,
  for PythonConfluenceAPI, and it doesn't come with the pip
  PythonConfluenceAPI. This is not the "right" way to do this, but it works so
  far

### General/Notebook Usage
* Make the environment (assuming Anaconda is installed and on the path)
`conda create --name atlassian_rest python=3 tornado jupyter notebook pep8`
* Activate the environment
`source activate atlassian_rest`
* Install new packages (as needed...should be documented here if not already)
`conda install --name atlassian_rest [packages]` or `pip install [packages]`
* Run notebook server (blocking) `jupyter notebook --port [port_num]`
* Load the notebook 'Atlassian REST API Sandbox'
* Have fun. Run the cells in order. Hopefully I'll have time to document things
  in the notebook better soon.

### General TODO
* Determine what doc building method/format to use, and use it!

### Notes
* Tested against Confluence 5.9.6
* Test the REST API is available with:
  `curl -u username [BASE_URL]/rest/api/content` where BASE_URL is something
  like: `https://[ATLASSIAN_SERVER]/confluence`. You'll be prompted for a
  password for user `username`. The response should be a bunch of content (
  pages and such).
