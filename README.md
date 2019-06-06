# Pleonastic Pronoun detection

This is the code used for the Bachelor thesis of [Bertelt Braaksma](mailto:b.braaksma.1@student.rug.nl). The aim of the research was to create a pleonastic pronoun detector, using a Random Forest Classifier. We trained the classifier on the SoNaR1 corpus.

## Requirements

* DutchCoref
* sklearn
* pandas

Our final program is a modified version of [the DutchCoref system](https://github.com/andreasvc/dutchcoref/) and requires a working installation of that program to work. Please follow the instructions provided in the readme to get the software up and running.

### Installation
As mentioned above, please go to [DutchCoref](https://github.com/andreasvc/dutchcoref/) first and get it up and running. After that, you can clone our repository and install the requirements as follows:

```
$ git clone https://github.com/barfsma/newcoref.git
$ cd newcoref
$ pip3 install -r requirements.txt
```

Once the dependencies have been installed, please copy the file `new_coref.py` and the folder `pleonastic` to your DutchCoref installation folder. The folder `other` contains scripts which were used for the development of the system. If you wish to reproduce our research, please copy the contents of this folder to your DutchCoref installation location as well.
