# Seasonal Woodland

## Authors
Simone Sechi

* Audio Classification and graphical interface

Rebecca Superbo

* Graphical interface and sound design

Pierluigi Tartabini

* Musical composition and sound design
## Abstract
An artistic installation that enables children to play and discover music feelings and sensations through interaction and visualization.
## Description
Seasonal Woodland is thought to be an artistic installation following a full-fledged conversational model, involving sound and visual interaction. The target audience are children (of at least 4 years old) and the learning curve is zero, as the only requested action is that of hitting a wooden board with two different sticks, which will change the entire auditive and visive scenario.

Our goals are:

* To make children play while witnessing to musical and graphical changes.
* To make them understand basic concepts of musical consonance and dissonance and relating those to the concept of the changing of seasons.

## How it works
There are 3 components: the children, the wood board and 2 sticks, that' re different for their top : in a stick we have an heart and in the second one we have a sphere. The batons are the objects wich the children will compose his/her music and changes the visualization,in fact the batons hit have 2 consequences, in particular:

* **heart stick** : hitting the wood board with this baton directs the music composition in a prodcution of squeaky audio; in particular they will be produced diminuished chords in backgrounds and a melody taken fro randomly long intervals from the scale of the chord. In the visualization part the children will see the autumn season with the leaves movement; their trajectories are like disturbed and almost uncorrelated. They have primary color to simulate autumn behaviours.

* **sphere stick** : hitting the wood board with this baton directs the music composition in a prodcution of a major background chords with a melody composed by unitary intervals starting from the tonal or the third. In the visualization part the autumn season becomes spring, and the previous leaves are transformed into butterflies. These animals has an harmonious movement, coordinated between them; furthermore if they meeet each other, they aggregate theirselves into groups.
 

## Technology
Python: audio classification and musical composition.

Supercollider: sound design.

Processing: graphical interface.
## How to run locally

### Step 1
To try the Seasonal Woodland in your pc you have, first of all, to have installed Pyton,Processing and Supercollider.
For the hardware part you have to get a :
* wood table that will be hitten.
* two types of different sticks to strike the table.
* one or more piezo to detect the hits.
* an audio card that transmits the strikes to the pc.

### Step 2
Before running the project you have to train your audio classification script; we recommend you  to strike the table sequentially with a metronome beat,store the audio with a digital audio workstation ( like Reaper) and train your script with the extracted data.

### Step 3
You have to initialize the NetAddress ( and the relative port), the synthetizers,the OscReciever and the OscFunc in Supercollider to allow the comunication between Python and Supercollider. After that you have to run the main.py file and (......); once you did it you can start playing with the Seasonal Woodland.


## License
