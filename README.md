Pubstandards London
===================

How to add Substandards events, or more PS event details
--------------------------------------------------------
Open ```ps_data.json```, add a new entry for the event - the format is fairly self-documenting.

If you're adding more information about an event, just use the same date as the automatically generated one and specify the fields you want to override. Look at PS C and PS LXVI for examples.

The website build process will attempt to automatically geocode (lookup coordinates) for any new locations. If a map isn't displayed on the event page, or it's wrong, you can manually add coordinates in [locations.json](./locations.json).

How to hack on this website
---------------------------
* Install [uv](https://docs.astral.sh/uv/)
* Check out the repository
* Start the dev server with `uv run ./ps.py`
* Open a browser to [http://localhost:5000](http://localhost:5000)
* Hack away!
* Run the tests with `uv pytest .`
* Open a pull request, then prod someone else to check it before merging

The code and templates will live reload, and Flask will drop you into a lovely interactive exception inspector if you do a bad.
