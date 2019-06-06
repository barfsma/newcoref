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

Once the dependencies have been installed, please copy the file `new_coref.py` and the folder `pleonastic` to your DutchCoref installation folder. Our script should be called in exactly the same way as `coref.py` from DutchCoref.

## Replicating research
The folder `other` contains scripts which were used for the development of the system. If you wish to replicate our research, please copy the contents of this folder to your DutchCoref installation location as well. Unfortunately, the two corpora we used for our research contain copyrighted material. As we are not allowed to redistribute copyrighted material, we could not include some files that are essential in order to replicate our research. Therefore, the `sonar` and `riddlecoref` folders are empty, but we did did include the code we used during development. You could still get a hold of the corpora through other means, such as [the website of SoNaR](https://ivdnt.org/downloads/tstc-sonar-corpus).
