[![Build Status](https://travis-ci.org/mjbommar/amos3.svg?branch=master)](https://travis-ci.org/mjbommar/amos3) [![Coverage Status](https://coveralls.io/repos/github/mjbommar/amos3/badge.svg)](https://coveralls.io/github/mjbommar/amos3)

# amos3
#### Python 3 client for Archive of Many Outdoor Scenes (AMOS)
amos3 is a Python 3 client for the Archive of Many Outdoor Scenes (AMOS) that includes:
* methods to retrieve lists of cameras and related metadata
* methods to retrieve lists of images by camera
* methods to retrieve raw images by camera/timestamp
* methods to retrieve monthly ZIP archives of images by camera
* comprehensive unit tests with near-complete coverage


## What is AMOS?
[AMOS](http://amos.cse.wustl.edu/) is a project of [Media and Machines Lab](http://www.cse.wustl.edu/MediaAndMachines) at the Washington University in St. Louis.  In their own words,
> AMOS is a collection of long-term timelapse imagery from publicly accessible outdoor webcams around the world. We explore how to use
> these images to learn about the world around us, with a focus on understanding changes in natural environments and understanding how
> people use public spaces.

AMOS contains over 1 billion images from nearly 30K cameras over more than 15 years (as of June 2018).

**This repository and its author are not affiliated with AMOS or WashU.**

## amos3 Roadmap
This initial release supports core functionality required to create simple datasets from AMOS on modern Python distributions.  Subsequent releases will include more functionality to automate the creation of datasets.  Integration with PIL/Pillow is also being considered to simplify the generation of standardized inputs for machine learning/computer vision applications.


## Information
* GitHub repository: https://github.com/mjbommar/amos3/
* Documentation: In Progress
* Contact: [GitHub Issues](https://github.com/mjbommar/amos3/issues)

## Licensing
amos3 is distributed under the standard OSI MIT License (Expat) as documented in the repository LICENSE file.

## Releases
| Release | Date | Description |
| --- | --- | --- |
| 0.1.0 | 2018-06-27 | initial public release |
