# Bgmodel
This is the basal ganglia model used in the paper 
["Untangling basal ganglia network dynamics and function – role of dopamine depletion and inhibition investigated in a spiking network model"](http://eneuro.org/content/early/2016/12/22/ENEURO.0156-16.2016.article-info),
It build using [pyNEST](http://www.nest-simulator.org/introduction-to-pynest/) that under the 
hood utilize the [NEST simulator](http://www.nest-simulator.org/). The model have been run Nest 2.6 see [nest download](http://www.nest-simulator.org/download/).

##Installation

Dependencies:
* python: numpy, scipy, mpi4py, NeuroTools (0.2.0), psycopg2
others: openmpi, libncurses-dev, libreadline-dev, libopenmpi-dev, libgsl, gsl (gnu scitific library, solver, neccesary for module) 

Dependencies module
* autoconf, automake


clone the repository

```
git clone https://github.com/mickelindahl/bgmodel.git
```

To install both nest and the model ooen terminal and enter 
```
cd {path to model}/dist
./install_nest_2.12_and_module_2.12.sh
```

Else to only install the model with prevoius nest installtion
```
cd {path to model}/module/compile-module-2.12.0.sh {path to nest installation}
```

Copy `sample.env` to `.env`
```
cp sample.ev .env
```
 
```sh
PYNEST=/home/mikael/opt/NEST/dist/install-nest-2.2.2/lib/python2.7/site-packages/
export PYTHONPATH=$PYTHONPATH:$PYNEST
```
















