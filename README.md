TTC-Aliens
==========

This is a simple twitter bot that occasionally 'aleinfies' tweets from a transit system. It was built with the TTC in mind
but can easily be expanded to other services and accounts.

On the surface, it appears to reiterate the same tweets as a source account, in our case, the TTC's TTCnotices account.
However, occasionally it will change the cause of a delay or problem to something more alien or conspiracy related.

**As an example**

Source tweet:
- 511 Bathurst route turning back northbound via King, Spadina, Queen due to a collision on Bathurst at Front. #TTC

Resulting tweet:
- 511 Bathurst route turning back northbound via King, Spadina, Queen due to aliens.#TTC
  

Requirements
------------
Python 2.7
python-twitter (and its dependencies) - http://code.google.com/p/python-twitter/

Installation
------------
Git clone and run once and close it. 
It will create a setup.ini file. 
Update this file with your twitter api and oauth keys.
Modify the ttc_twitter.py file to change constants as needed.

TODO
----
1. Changes around intallation / setup process. It is clunky and ugly, I know.
2. Fix tweeting replies
3. Fix calculation of odds (it's not mathematically ideal right now, resulting in less than the prescribed chance)
4. Moar testing
5. GUI interface
6. Service abilities
7. profit?

Known issues
------------

Who knows? This has barely been tested and there are many potential issues
For example, replies are not filtered out, which is probably not ideal. 
Feel free to submit enhancements, bug reports, complaints, and love letters. 
