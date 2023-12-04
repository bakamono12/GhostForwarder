import pyrogram
import os
from time import sleep

# set the environment variables

api_id = os.environ.get("API_ID", None)
api_hash = os.environ.get("API_HASH", None)

# create a pyrogram session
app = pyrogram.Client("ghost-forwarder", api_id=api_id, api_hash=api_hash)

# start the pyrogram session
app.start()
print(app.export_session_string())
sleep(15)  # wait for 15 seconds before closing the session after the authentication
app.stop()
# FAQ: In Case the session is not created.
# A session is created inside the repo [ghost-forwarder.session] if not rerun the
# process and remove the sleep() and stop() function or comment them out.
