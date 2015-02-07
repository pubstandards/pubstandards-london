Pubstandards London
===================

How to add Substandards events, or more PS event details
--------------------------------------------------------
Open ```ps_data.json```, add a new entry for the event - the format is fairly self-documenting.

If you're adding more information about an event, just use the same date as the automatically generated one and specify the fields you want to override. Look at PS C and PS LXVI for examples.

NOTE: It is important that the items stay in date order, so make sure of that before committing/pushing.

How to hack on this website
---------------------------
* Check out the repository
* ```pip install -r requirements.txt``` (You probably want to do this in a virtualenv)
* ```python ps.py```
* Open a browser to [http://localhost:5000](http://localhost:5000)
* Hack away!
* Prod a PS regular (Norm, James, Jonty, etc) for commit access, or fork
* Commit, open a pull request, then prod someone else to check it before merging

The code and templates will live reload, and Flask will drop you into a lovely interactive exception inspector if you do a bad.
