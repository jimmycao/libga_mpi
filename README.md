libga_mpi
=========
C++ and Python sources to use Genetic Algorithms that can be parallelized via MPI (island model). 

What it is and what is not
--------------------------
The C++ and Python versions are independent. For viewing optimization results you might want to take advantage of some Python (Matplotlib) scripts, though. You need a compiler supporting parts of C++11 if you want to compile the examples. For running the Python examples Python 2.7 (plus the usual set of libraries, see introductory PDF) is sufficient. The flavor if MPI is probably irrelevant since -intentionally- only very basic operations are used. 

The goal of libga_mpi is not to provide an exhaustive and complicated survey of genetic algorithm techniques. Rather, just a limited set of easy to use algorithms (SPEA2 for multi-objective problems and a "standard" genetic algorithm for single-objective problems) are provided. A few test problems have been implemented in both Python and C++. 

The same principle applies to the way the algorithms are parallalized: there are way more performant options out there. This library only uses what is necessary to elegantly distibute work via MPI. This is easier to read and debug but still provides a fully working parallel island model. 

It is optional to use the parallel versions of the algorithms. Going from a single process to multi-processing is just a matter of changing a few lines because a simple, consistent interface is maintained. Also the interfaces of the Python and C++ versions are very similar to facilitate prototyping in Python and converting to C++ for speed. 
The Python version is generic enough to allow for "non-traditional" genome types e.g. sets of trees. However, only genetic operators (crossover, mutation etc) for the typical real-valued genome are provided. The C++ version requires the genome type to be a real-valued matrix. This helps keeping the C++ source communicating via MPI simple. 

Where to start
--------------
To build (make) the short and introductory PDF documentation which is more of a guide of how to run the Python and C++ examples and what to expect from libga_mpi. 

For the impatient, have a look at the examples/ directory where you will find a couple of shell scripts that build and run specific test problems. This source also contains a few Python scripts to merge and visualize the algorithms' results. 

The MIT License (MIT)
---------------------
Copyright (c) 2013 Martin Wirth

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
